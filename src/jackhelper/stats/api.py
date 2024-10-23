from django.http import JsonResponse

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
        block = Stats(city, start_date, end_date).getMetrics(block_id)
    except ValueError:
        return JsonResponse(
            {'errors': [{
                'text': f'Запрошен неизвестный блок статистических метрик. ID блока: {block_id}'
            }]},
            status=404,
        )
    
    return JsonResponse(block, status=200)