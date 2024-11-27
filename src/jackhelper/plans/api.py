from django.http import HttpResponse, JsonResponse

from jackhelper import redis_client
from .models import Plan
from .plans import getMonthPlan

import json
import datetime


def setMonthPlan(request):
    city = request.POST.get('city')
    year = request.POST.get('year')
    month = request.POST.get('month')

    revenue = request.POST.get('revenue')
    works_revenue = request.POST.get('works_revenue')
    spare_parts_revenue = request.POST.get('spare_parts_revenue')
    normal_hours = request.POST.get('normal_hours')
    metrics = [revenue, works_revenue, spare_parts_revenue, normal_hours]

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
        plan.normal_hours = normal_hours
        plan.save()
        plan_status = 'changed'
    except Plan.DoesNotExist:
        Plan.objects.create(
            city=city, 
            year=year, 
            month=month,
            revenue=revenue, 
            works_revenue=works_revenue, 
            spare_parts_revenue=spare_parts_revenue,
            normal_hours=normal_hours
        )
        plan_status = 'created'

    match plan_status:
        case 'created': http_status = 201
        case 'changed': http_status = 200

    cached_metrics_redis_key = f'jackhelper-plan-{city}_{year}_{month}-metrics'
    if redis_client.getValue(cached_metrics_redis_key):
        redis_client.delKey(cached_metrics_redis_key)

    return JsonResponse(
        {'city': city, 'year': year, 'month': month}, status=http_status
    )


def getAvailableMonths(request):
    city = request.GET.get('city')
    year = request.GET.get('year')

    current_month = datetime.datetime.now().month
    if current_month <= 6:
        month_ordering = 'month'
    else:
        month_ordering = '-month'

    available_months = [
        i.month for i in Plan.objects.only('month').order_by(month_ordering).filter(city=city, year=year)
    ]
    return JsonResponse({'available_months': available_months}, status=200)


def getPlanMetrics(request):
    city = request.GET.get('city')
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    cached_metrics_redis_key = f'jackhelper-plan-{city}_{year}_{month}-metrics'
    if cached_metrics := redis_client.getValue(cached_metrics_redis_key):
        metrics = json.loads(cached_metrics)
    else:
        try:
            metrics = getMonthPlan(city, year, month)
        except ValueError:
            return HttpResponse('Unavailable plan month', status=404)

        now = datetime.datetime.now()
        if year == now.year and month == now.month:
            cached_metrics_expiration_seconds = (60**2)*3 # 3 hours
        else:
            cached_metrics_expiration_seconds = (60**2)*24 # 1 day
        redis_client.setValue(
            cached_metrics_redis_key, 
            json.dumps(metrics), 
            expiration=cached_metrics_expiration_seconds
        )

    return JsonResponse(
        {   
            'city': city,
            'year': year,
            'month': month,
            'metrics': metrics
        }, 
        status=200
    )


def getAnnualPlanMetrics(request):
    city = request.GET.get('city')
    year = request.GET.get('year')

    annual_plan = {
        'metrics': {},
        'monthly_plans': {},
    }

    cached_plan_redis_key = f'jackhelper-annual_plan-{city}_{year}'
    if cached_annual_plan := redis_client.getValue(cached_plan_redis_key):
        annual_plan = json.loads(cached_annual_plan)
    else:
        for month in range(1, 12+1):
            cached_metrics_redis_key = f'jackhelper-plan-{city}_{year}_{month}-metrics'
            if cached_metrics := redis_client.getValue(cached_metrics_redis_key):
                metrics = json.loads(cached_metrics)
            else:
                try:
                    metrics = getMonthPlan(city, year, month)
                except ValueError:
                    continue
            annual_plan['monthly_plans'][month] = metrics
            for metric in metrics:
                metric_id = metric['id']

                if metric_id not in annual_plan['metrics'].keys():
                    annual_plan['metrics'][metric_id] = metric
                else:
                    annual_plan['metrics'][metric_id]['plan_value'] += metric['plan_value']
                    annual_plan['metrics'][metric_id]['current_value'] += metric['current_value']

    redis_client.setValue(
        cached_plan_redis_key, 
        json.dumps(annual_plan), 
        expiration=(60**2)*24 # 1 day
    )

    return JsonResponse(
        {   
            'city': city,
            'year': year,
            'plan': annual_plan,
        }, 
        status=200
    )