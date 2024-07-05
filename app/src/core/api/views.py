from rest_framework.decorators import api_view
from rest_framework.response import Response

import datetime

from src.core import models
from src.core.api import serializers


@api_view(['GET'])
def get_quarters(request, format=None):
    request_url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"

    try:
        scoring = models.Scoring.objects.filter(type='Q')

        serializer = serializers.ScoringSerializer(scoring, many=True)

        json_response = {
            'url': request_url,
            'success': True,
            'error': '',
            'count': len(serializer.data),
            'unique_timestamps': sorted(set(item['timestamp'] for item in serializer.data)),
            'scoring': serializer.data
        }
    except Exception as error:
        json_response = {
            'url': request_url,
            'success': False,
            'error': str(error).strip(),
            'count': 0,
            'unique_timestamps': [],
            'scoring': []
        }

    return Response(json_response)


@api_view(['GET'])
def get_weeks(request, quarter, format=None):
    request_url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"

    try:
        start_of_quarter, end_of_quarter = (part.strip() for part in quarter.split(':')[-1].split('-'))
        start_of_quarter, end_of_quarter = (datetime.datetime.strptime(start_of_quarter, '%Y.%m.%d'),
                                            datetime.datetime.strptime(end_of_quarter, '%Y.%m.%d'))

        weeks = []
        for week in models.Scoring.objects.filter(type='W'):
            start_of_week, end_of_week = (part.strip() for part in week.timestamp.split(':')[-1].split('-'))
            start_of_week, end_of_week = (datetime.datetime.strptime(start_of_week, '%Y.%m.%d'),
                                          datetime.datetime.strptime(end_of_week, '%Y.%m.%d'))

            if start_of_quarter <= start_of_week <= end_of_quarter and start_of_quarter <= end_of_week <= end_of_quarter:
                weeks.append(week.id)

        scoring = models.Scoring.objects.filter(type='W', id__in=weeks)

        serializer = serializers.ScoringSerializer(scoring, many=True)

        json_response = {
            'url': request_url,
            'success': True,
            'error': '',
            'count': len(serializer.data),
            'unique_timestamps': sorted(set(item['timestamp'] for item in serializer.data)),
            'scoring': serializer.data
        }
    except Exception as error:
        json_response = {
            'url': request_url,
            'success': False,
            'error': str(error).strip(),
            'count': 0,
            'unique_timestamps': [],
            'scoring': []
        }

    return Response(json_response)


@api_view(['GET'])
def get_days(request, week, format=None):
    request_url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"

    try:
        start_of_week, end_of_week = (part.strip() for part in week.split(':')[-1].split('-'))
        start_of_week, end_of_week = (datetime.datetime.strptime(start_of_week, '%Y.%m.%d'),
                                      datetime.datetime.strptime(end_of_week, '%Y.%m.%d'))

        days = []
        for day in models.Scoring.objects.filter(type='D'):
            day_timestamp = datetime.datetime.strptime(day.timestamp, '%Y.%m.%d')

            if start_of_week <= day_timestamp <= end_of_week:
                days.append(day.id)

        scoring = models.Scoring.objects.filter(type='D', id__in=days)

        serializer = serializers.ScoringSerializer(scoring, many=True)

        json_response = {
            'url': request_url,
            'success': True,
            'error': '',
            'count': len(serializer.data),
            'unique_timestamps': sorted(set(item['timestamp'] for item in serializer.data)),
            'scoring': serializer.data
        }
    except Exception as error:
        json_response = {
            'url': request_url,
            'success': False,
            'error': str(error).strip(),
            'count': 0,
            'unique_timestamps': [],
            'scoring': []
        }

    return Response(json_response)


@api_view(['GET'])
def get_intervals(request, day, format=None):
    request_url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"

    public_key = request.GET.get('public_key', None)

    try:
        if public_key is not None:
            day = datetime.datetime.strptime(day, '%Y.%m.%d')

            score = models.Score.objects.filter(node__public_key=public_key.strip().lower(), timestamp__date=day)

            serializer = serializers.ScoreSerializer(score, many=True)

            json_response = {
                'url': request_url,
                'success': True,
                'error': '',
                'count': len(serializer.data),
                'unique_timestamps': sorted(set(item['timestamp'] for item in serializer.data)),
                'scoring': serializer.data
            }
        else:
            json_response = {
                'url': request_url,
                'success': False,
                'error': 'No public key provided',
                'count': 0,
                'unique_timestamps': [],
                'scoring': []
            }
    except Exception as error:
        json_response = {
            'url': request_url,
            'success': False,
            'error': str(error).strip(),
            'count': 0,
            'unique_timestamps': [],
            'scoring': []
        }

    return Response(json_response)
