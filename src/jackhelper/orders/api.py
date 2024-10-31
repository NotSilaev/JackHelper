from django.http import HttpResponse, JsonResponse

from stats.utils import ifNoneGetDefaultValues
from .orders_list import getOrdersCountAndList

import math
import json


def getOrders(request):
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tags = request.GET.get('tags')
    if tags: tags = tuple(json.loads(tags))
    search = request.GET.get('search')
    page = request.GET.get('page')
    if page is not None: page = int(page)
    else: page = 1
    offset = 20

    city, start_date, end_date = ifNoneGetDefaultValues(city, start_date, end_date)

    try:
        orders_count, orders_list = getOrdersCountAndList(city, start_date, end_date, search, tags, offset, page)
    except ValueError as e:
        return JsonResponse(
            {'errors': [{'text': str(e)}]},
            status=400
        )

    if orders_count == 0:
        return JsonResponse({
            'orders': {'count': 0},
            'pagination': {'pages_count': 0, 'current_page': 0},
        }, status=201)
    pages_count =  math.ceil(orders_count / offset)

    return JsonResponse({
        'orders': {
            'count': orders_count,
            'list': orders_list,
        },
        'pagination': {
            'pages_count': pages_count,
            'current_page': page,
        },
    }, status=200)
