from django.http import JsonResponse

from jackhelper import redis_client
from .stats import Stats
from .utils import ifNoneGetDefaultValues

import datetime


def getStatsBlock(request):
    block_id = request.GET.get('block_id')
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    city, start_date, end_date = ifNoneGetDefaultValues(city, start_date, end_date)

    try:
        cached_block_redis_key = f'jackhelper-stats-{block_id}-{city}-{start_date}-{end_date}'
        if cached_block := redis_client.getValue(cached_block_redis_key):
            block = cached_block
        else:
            block = Stats(city, start_date, end_date).getMetrics(block_id)

            now = datetime.datetime.now()
            if start_date == now.date() or end_date == now.date():
                cached_block_expiration_seconds = 60*60*3 # 3 hours
            else:
                cached_block_expiration_seconds = 60*60*24 # 1 day
            redis_client.setValue(
                cached_block_redis_key,
                block,
                expiration=cached_block_expiration_seconds,
            )
    except ValueError:
        return JsonResponse(
            {'errors': [{
                'text': f'Запрошен неизвестный блок статистических метрик. ID блока: {block_id}'
            }]},
            status=404,
        )
    
    return JsonResponse(block, status=200)