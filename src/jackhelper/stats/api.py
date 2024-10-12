from django.http import JsonResponse

from .stats import Stats

import datetime


def getStatsBlock(request):
    block_id = request.GET.get('block_id')
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if city is None: city = 'VLG'

    if start_date is None: start_date = datetime.date.today()
    else: start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date is None: end_date = start_date
    else: end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

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