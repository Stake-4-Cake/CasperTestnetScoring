# Casper Testnet Monitoring Service

### Algorithm

_The cycle consists of the steps below are being executed every 05:00 minutes and according to my observations 
take up to 30 seconds to be executed_

**1. Collection of public keys, current height and peers.**  
    By sending a request to the endpoint http://<ip>:8888/status from each node which IP is contained in the Database 
    after the completion of the previous cycle, the following are collected and recorded in the Database:  
        - public key;  
        - the current height of the block;  
        - IP addresses of peers;  
    The maximum waiting time for a response from nodes is 10 seconds.

**2. Determination of the reference maximum height of the block.**  
    The heights of the blocks of each node recorded in the Database in step 1 are compared with each other, as a result 
    of which the reference maximum height of the block available 
    in the network at the time of the survey is determined (chain tip).

**3. Receiving auction info.**  
    By sending an RPC request with the state_get_auction_info method to https://rpc.testnet.casperlabs.io/rpc, we get 
    all the validators and all the bids in the network for the current era.

**4. Finding network weight and all (100) validators.**  
    We add up all the weights of each validator and get the network weight. 
    Also, we keep all validators' public keys for the current era.

**5. Storing auction data for each node.**  
    For each public key, we record in the Database the bid status (active/inactive), total stake and for 
    active validators also percent of network.

**6. Determination of Scoring for a 5-minute interval.**  
    For each public key recorded in the Database in step 2, we record the value of the scoring True, in case:  
        - The block height of this public key is not less than maximum height - 4, and  
        - This public key has an active bid  
    Also, percent_of_share, total_stake and network_weight are recorded.

**7. Determination of current/daily scoring.**  
    The current daily scoring is calculated in % as (active_scores / max_scores) * 100 during each 
    5 minute interval and recorded in the Database. Also, during each 5-minute interval, a check is performed 
    for percent of network exceeding 6%. If the node exceeded this limit at least once per day, 
    then the value True is stored in the stake_over field in the Scoring Database.  
    Longevity is calculated every day as follows:  
        - If the score at the end of the day N < 90, then the longevity is reset;
        - Otherwise, the longevity is updated by increasing the longevity at the end of the N - 1 day by the value 
        of the score obtained for the N day.

**8. Determination of weekly scoring.**  
    The number of points scored during the week is calculated as the sum of points scored for each day of this week 
    and multiply by 0.9 if at least one True value was recorded in the stake_over field of the Scoring Database 
    for this node during the week.

**9. Determination of nodes entitled to receive rewards.**  
    After determining the weekly scoring, nodes are sorted in descending order, first by weekly scoring and 
    then by longevity. For the first 100 nodes in the sorted list, the value Yes is written to the Eligible for 
    Rewards field in the Database.

**10. Determination of total rewards for the quarter.**  
    Rewards for a quarter are defined as the sum of rewards for the weeks included in that quarter.
