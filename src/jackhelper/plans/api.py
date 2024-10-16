from django.http import HttpResponse, JsonResponse

from .models import Plan
from .utils import daysUntilNextMonth
from stats.stats import Stats

import datetime


def setMonthPlan(request):
    city = request.POST.get('city')
    year = request.POST.get('year')
    month = request.POST.get('month')

    revenue = request.POST.get('revenue')
    works_revenue = request.POST.get('works_revenue')
    spare_parts_revenue = request.POST.get('spare_parts_revenue')
    metrics = [revenue, works_revenue, spare_parts_revenue]

    if False in list(map(str.isnumeric, metrics)):
        return JsonResponse({'errors': [
            {'text': 'Все метрики должны быть целыми числами'}
        ]}, 
        status=400)

    try:
        plan = Plan.objects.get(city=city, year=year, month=month)
        plan.revenue = revenue
        plan.works_revenue = works_revenue
        plan.spare_parts_revenue = spare_parts_revenue
        plan.save()
        plan_status = 'changed'
    except Plan.DoesNotExist:
        Plan.objects.create(
            city=city, 
            year=year, 
            month=month,
            revenue=revenue, 
            works_revenue=works_revenue, 
            spare_parts_revenue=spare_parts_revenue
        )
        plan_status = 'created'

    match plan_status:
        case 'created': http_status = 201
        case 'changed': http_status = 200

    return JsonResponse(
        {'city': city, 'year': year, 'month': month}, status=http_status
    )


def getAvailableMonths(request):
    city = request.GET.get('city')
    year = request.GET.get('year')
    
    available_months = [
        i.month for i in Plan.objects.only('month').order_by('-month').filter(city=city, year=year)
    ]
    current_month = datetime.datetime.now().month
    if current_month in available_months:
        current_month_index = available_months.index(current_month)
        month_plan = available_months.pop(current_month_index)
        available_months.insert(0, month_plan)
    
    return JsonResponse({'available_months': available_months}, status=200)


def getPlanMetrics(request):
    city = request.GET.get('city')
    year = request.GET.get('year')
    month = request.GET.get('month')

    try:
        plan = Plan.objects.only(
            'revenue', 'works_revenue', 'spare_parts_revenue'
        ).get(city=city, year=year, month=month)
    except Plan.DoesNotExist:
        return HttpResponse('Unavailable plan month', status=404)

    
    start_date = datetime.datetime.strptime(f'{year}-{month}-1', '%Y-%m-%d')
    end_date = start_date + datetime.timedelta(days=daysUntilNextMonth(start_date)-1)
    finance_metrics = Stats(
        city, start_date.date(), end_date.date()
    ).getMetrics('finance', short_output=True)['metrics']

    current_revenue = finance_metrics[0]['value']
    current_works_revenue = finance_metrics[1]['value']
    current_spare_parts_revenue = finance_metrics[2]['value']

    metrics = [
        {
            'title': 'Выручка', 
            'plan_value': plan.revenue, 
            'current_value': current_revenue
        },
        {
            'title': 'Выручка с работ', 
            'plan_value': plan.works_revenue, 
            'current_value': current_works_revenue
        },
        {
            'title': 'Выручка с з/ч', 
            'plan_value': plan.spare_parts_revenue, 
            'current_value': current_spare_parts_revenue
        },
    ]

    return JsonResponse(
        {   
            'city': city,
            'year': year,
            'month': month,
            'metrics': metrics
        }, 
        status=200
     )
