import os
import django
import asyncio
import datetime
import aiohttp
from bs4 import BeautifulSoup
import time
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from django.conf import settings
from src.core import models


async def get_status(ip: str) -> (str, dict,):
    """Gets status endpoint response for Casper Testnet node using given IP address."""

    try:
        # Use Aiohttp session to make async requests
        async with aiohttp.ClientSession(
                headers=settings.CASPER_STATUS_HEADERS,
                trust_env=True,
                connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            resp = await session.request(
                method='GET',
                url=settings.STATUS_ENDPOINT_URL.format(ip),
                timeout=10  # Wait response for 10 seconds
            )
            resp_json = await resp.json()
        return ip, resp_json
    except Exception as error:
        # Return dict with error if node does not respond
        return ip, {'error': str(error).strip()}


async def get_cnm_ips(session) -> set:
    """Gets Casper Testnet network node's IP addresses from CNM."""

    ips = set()

    try:
        resp = await session.request(
            method='GET',
            url=settings.TRUSTED_RPC,
            timeout=30
        )
        resp_text = await resp.text()
        soup = BeautifulSoup(resp_text, 'lxml')

        # Scrape CNM HTML page and collect IPs
        for ip in soup.find_all('tr')[1:]:
            ips.add(ip.find('td').text.strip())
    except Exception:
        pass

    return ips


async def update_peers() -> None:
    """Updates all Casper Testnet peers from CNM in Database."""

    peers = set()

    async with aiohttp.ClientSession(
            headers=settings.CNM_HEADERS,
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        cnm_ips = await get_cnm_ips(session)
        peers.update(cnm_ips)

    print(datetime.datetime.now(), 'Peers From CNM:', len(peers))

    for peer in peers:
        # Add peer to Database if it does not exist there
        if not models.Node.objects.filter(ip=peer).exists():
            models.Node.objects.create(ip=peer)


async def get_auction_info(session) -> dict:
    """Gets auction info RPC endpoint response for Casper Testnet."""

    # Prepare request payload
    payload = json.dumps({
        "id": 1,
        "jsonrpc": "2.0",
        "method": "state_get_auction_info",
        "params": []
    })

    # Get auction info within 30 seconds (try 3 times)
    for _ in range(3):
        try:
            resp = await session.request(
                method='POST',
                url='https://rpc.testnet.casperlabs.io/rpc',
                data=payload,
                timeout=30
            )
            assert resp.status == 200
            resp_json = await resp.json()

            return resp_json
        except Exception:
            await asyncio.sleep(1)
    else:
        return {}


async def update_auction_info() -> None:
    """Updates auction info for all nodes present in Database."""

    async with aiohttp.ClientSession(
        headers={'Content-Type': 'application/json'},
        trust_env=True,
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        auction_info = await get_auction_info(session)

    # Check if an auction info is successfully fetched
    if not auction_info:
        return

    network_weight, validators = 0, set()

    # Calculate network weight and save validators' public keys
    for validator in auction_info['result']['auction_state']['era_validators'][0]['validator_weights']:
        network_weight += int(validator['weight'])
        validators.add(validator['public_key'].lower())

    print(datetime.datetime.now(), f'Network Weight {network_weight}, Validators {len(validators)}')

    for bid in auction_info['result']['auction_state']['bids']:
        # Update auction information for each node in Database
        for node in models.Node.objects.filter(public_key=bid['public_key'].strip().lower()):
            node.active_bid = not bid['bid']['inactive']
            node.network_weight = network_weight
            node.total_stake = (sum(int(delegator['staked_amount']) for delegator in bid['bid']['delegators']) +
                                int(bid['bid']['staked_amount']))
            node.percent_of_network = (node.total_stake * 100) / network_weight if node.public_key in validators else 0
            node.save()


async def monitoring_score() -> None:
    """Monitoring score for all nodes present in Database."""

    # Get all IP addresses from Database
    peers, new_peers = set(models.Node.objects.all().values_list('ip', flat=True)), set()

    # If there are no IP addresses in Database, then update Database with IP addresses scraped from CNM
    # Will be executed only at the first launch
    if not peers:
        await update_peers()

        peers = set(models.Node.objects.all().values_list('ip', flat=True))

    print(datetime.datetime.now(), f'Fetched {len(peers)} Peers')

    # Create array with future tasks, will be executed asynchronously
    # Where task is get status endpoint for each IP address
    tasks = (asyncio.create_task(get_status(ip)) for ip in peers)

    # Gather all tasks' responses in array
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    print(datetime.datetime.now(), f'Got {len(responses)} Statuses')

    for ip, resp in responses:
        # Get Public Key and Height from status endpoint response for each IP if not exists then empty

        try:
            pk = resp['our_public_signing_key'].strip().lower()
        except Exception:
            pk = ''

        try:
            height = int(resp['last_added_block_info']['height'])
        except Exception:
            height = 0

        # Save Public Key and Height in Database
        node = models.Node.objects.get(ip=ip)
        if pk:
            node.public_key = pk
        node.height = height
        node.save()

        # If node has peers then collect them in set
        if 'peers' in resp:
            for peer in resp['peers']:
                new_peer = peer['address'].split(':')[0]
                new_peers.add(new_peer)

    print(datetime.datetime.now(), f'Found {len(new_peers)} New Peers')

    for peer in new_peers:
        # If peer does not exist in Database, so add it there
        if not models.Node.objects.filter(ip=peer).exists():
            models.Node.objects.create(ip=peer)

    # Determine maximum height at the network currently
    max_height = max(models.Node.objects.all().values_list('height', flat=True))

    print(datetime.datetime.now(), f'Max Height {max_height}')

    await update_auction_info()

    print(datetime.datetime.now(), 'Bids Fetched')

    timestamp_now = datetime.datetime.now()

    for node in models.Node.objects.exclude(public_key=''):
        # Create new Score object in Database for each public key for current 5 minute interval
        # Field `active` means that at current interval the public key
        # has height within 4 block of maximum height and active bid
        # The following information is also saved in Database for current interval:
        # current height, network weight, total stake, is active bid and percent of network
        models.Score.objects.create(
            node=node,
            current_block=node.height,
            network_weight=node.network_weight,
            total_stake=node.total_stake,
            active_bid=node.active_bid,
            percent_of_network=node.percent_of_network,
            active=True if (max_height - node.height <= 4) and node.active_bid else False,
            timestamp=timestamp_now
        )


async def calculate_day_scoring():
    """Calculates current day scores for all public keys present in Database."""

    # Determine current day and previous day as datetime object
    day_now, previous_day = datetime.datetime.now().date(), datetime.datetime.now().date() - datetime.timedelta(days=1)

    print(datetime.datetime.now(), f'Make {day_now} Day Scoring')

    # Find max number of 5 minute intervals happened during current day
    max_scores = max(len(models.Score.objects.filter(node=node, timestamp__date=day_now))
                     for node in models.Node.objects.exclude(public_key=''))

    print(datetime.datetime.now(), f'Max Scores {max_scores}')

    for node in models.Node.objects.exclude(public_key=''):
        # Get all recorded scores that belongs to public key
        scores = models.Score.objects.filter(node=node, timestamp__date=day_now)

        # Find how many times the public key was active during current day
        active_scores = len(scores.filter(active=True))

        # Calculate public key's score for current day
        score = (active_scores / max_scores) * 100

        # Check if today was stake over 6% of network weight
        stake_over = scores.filter(percent_of_network__gte=6.0).exists()

        # If current day score < 90 at the end of the day, so reset longevity
        if score < 90 and max_scores == 288:
            longevity = 0
        else:
            # Try to get previous day longevity, if previous day longevity not found then consider it is 0
            if models.Scoring.objects.filter(node=node, timestamp=previous_day.strftime('%Y.%m.%d'), type='D').exists():
                scoring = models.Scoring.objects.get(node=node, timestamp=previous_day.strftime('%Y.%m.%d'), type='D')
                longevity = scoring.longevity
            else:
                longevity = 0

            # Update longevity with current day public key's score
            longevity += score

        # Get or create scoring object for public key, current day and save the following information:
        # current day score, current day longevity and if public key staked over 6%
        scoring = models.Scoring.objects.get_or_create(node=node, timestamp=day_now.strftime('%Y.%m.%d'), type='D')[0]
        scoring.score = score
        scoring.longevity = longevity
        if stake_over:
            scoring.stake_over = stake_over
        scoring.save()


async def _get_week(date):
    """Gets start-end week dates for given date."""

    start_of_week = date - datetime.timedelta(days=date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    week = (date.date() - datetime.datetime(date.year, (date.month - 1) // 3 * 3 + 1, 1).date()).days // 7 + 1
    week_now = f"W{week}: {start_of_week.strftime('%Y.%m.%d')} - {end_of_week.strftime('%Y.%m.%d')}"

    return start_of_week, end_of_week, week_now


async def calculate_week_scoring():
    """Calculates current week scores for all public keys present in Database."""

    start_of_week, end_of_week, week_now = await _get_week(datetime.datetime.today())

    print(datetime.datetime.now(), f'Make {week_now} Week Scoring')

    for node in models.Node.objects.exclude(public_key=''):
        score, stake_over, latest_day, longevity = 0, False, datetime.datetime.min, 0

        # Process each day in the Database for the public key
        for scoring in models.Scoring.objects.filter(node=node, type='D'):
            day = datetime.datetime.strptime(scoring.timestamp, '%Y.%m.%d')

            # Check if day belongs to curren week
            if start_of_week <= day <= end_of_week:
                # Current week score = sum of all daily scores in this week
                # Update current week score with day score
                score += scoring.score

                # Check if the public key at least one day staked over 6%
                if scoring.stake_over:
                    stake_over = True

                # Longevity at the end of the current week = longevity
                # at the end of the last day of the current week
                # Find the last day of current week and save its longevity
                if day > latest_day:
                    latest_day, longevity = day, scoring.longevity

        score /= 7

        # If public key staked over 6% at the current week then decrease its weekly score by 10%
        if stake_over:
            score *= 0.9

        # Save current week scoring for each public key
        scoring = models.Scoring.objects.get_or_create(node=node, timestamp=week_now, type='W')[0]
        scoring.longevity = longevity
        scoring.score = score
        if stake_over:
            scoring.stake_over = stake_over
        scoring.save()


async def determine_eligible_rewards():
    """Determines what public keys (100) are eligible for rewards at the current week"""

    start_of_week, end_of_week, week_now = await _get_week(datetime.datetime.today())

    print(datetime.datetime.now(), f'Determine {week_now} Week Eligible for Rewards')

    # Filter current week scoring and sort it in descending order by score then by longevity
    week_scoring_sorted = models.Scoring.objects.filter(type='W', timestamp=week_now).order_by('-score', '-longevity')

    # Mark first 100 as eligible for rewards, others not
    for index, scoring in enumerate(week_scoring_sorted):
        scoring.eligible_for_rewards = True if index < 100 else False
        scoring.save()


async def calculate_quarter_rewards():
    """Calculates current quarter rewards for all public keys present in Database."""

    # Get current quarter start-end dates as datetime object
    today = datetime.date.today()
    quarter = (today.month - 1) // 3 + 1
    match quarter:
        case 1:
            start_of_quarter, end_of_quarter = datetime.date(today.year, 1, 1), datetime.date(today.year, 3, 31)
        case 2:
            start_of_quarter, end_of_quarter = datetime.date(today.year, 4, 1), datetime.date(today.year, 6, 30)
        case 3:
            start_of_quarter, end_of_quarter = datetime.date(today.year, 7, 1), datetime.date(today.year, 9, 30)
        case 4:
            start_of_quarter, end_of_quarter = datetime.date(today.year, 10, 1), datetime.date(today.year, 12, 31)
    quarter_now = f"Q{quarter}: {start_of_quarter.strftime('%Y.%m.%d')} - {end_of_quarter.strftime('%Y.%m.%d')}"

    print(datetime.datetime.now(), f'Make {quarter_now} Quarter Scoring')

    for node in models.Node.objects.exclude(public_key=''):
        score, stake_over, latest_week, longevity = 0, False, datetime.datetime.min.date(), 0

        # Process each week in the Database for the public key
        for scoring in models.Scoring.objects.filter(node=node, type='W'):
            # Get week start-end dates as datetime object
            start_of_week, end_of_week = (part.strip() for part in scoring.timestamp.split(':')[-1].split('-'))
            start_of_week, end_of_week = (datetime.datetime.strptime(start_of_week, '%Y.%m.%d').date(),
                                          datetime.datetime.strptime(end_of_week, '%Y.%m.%d').date())

            # Check if week belongs to current quarter
            if start_of_quarter <= start_of_week <= end_of_quarter and start_of_quarter <= end_of_week <= end_of_quarter:
                # Update total quarter rewards with week rewards if public key is eligible for rewards in the week
                if scoring.eligible_for_rewards:
                    score += scoring.score

                if scoring.stake_over:
                    stake_over = True

                if start_of_week > latest_week:
                    latest_week, longevity = start_of_week, scoring.longevity

        # Save current quarter rewards for each public key
        scoring = models.Scoring.objects.get_or_create(node=node, timestamp=quarter_now, type='Q')[0]
        scoring.longevity = longevity
        scoring.score = score
        if stake_over:
            scoring.stake_over = stake_over
        scoring.eligible_for_rewards = True if score else False
        scoring.save()


async def main():
    print(datetime.datetime.now())

    start_time = time.time()

    await monitoring_score()

    await calculate_day_scoring()

    await calculate_week_scoring()

    await determine_eligible_rewards()

    await calculate_quarter_rewards()

    print(datetime.datetime.now(), time.time() - start_time, '\n')


# if __name__ == '__main__':
#     # asyncio.run(main())
#
#     while True:
#         if not datetime.datetime.now().minute % 5 and not datetime.datetime.now().second:
#             asyncio.run(main())
#         time.sleep(0.3)
