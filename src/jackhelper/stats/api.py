from django.http import JsonResponse

import datetime


def getStatsBlock(request):
    block_id = request.GET.get('block_id')
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if city is None: city = 'VLG'
    if start_date is None: start_date = datetime.date.today()
    if end_date is None: end_date = start_date

    blocks = {}
    try:
        block = blocks[block_id]
    except KeyError:
        return JsonResponse(
            {'errors': [{
                'text': f'Запрошен неизвестный блок статистических метрик. ID блока: {block_id}'
            }]},
            status=404,
        )
    
    return JsonResponse(block, status=200)