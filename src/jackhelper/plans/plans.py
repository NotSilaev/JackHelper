from stats.stats import Stats
from .models import Plan
from .utils import daysUntilNextMonth

import datetime


def getMonthPlan(city, year, month):
    try:
        plan = Plan.objects.only(
            'revenue', 'works_revenue', 'spare_parts_revenue'
        ).get(city=city, year=year, month=month)
    except Plan.DoesNotExist:
        raise ValueError('Unavailable plan month')

    start_date = datetime.datetime.strptime(f'{year}-{month}-1', '%Y-%m-%d')
    end_date = start_date + datetime.timedelta(days=daysUntilNextMonth(start_date)-1)

    stats_obj = Stats(city, start_date.date(), end_date.date())

    finance_metrics = stats_obj.getMetrics('finance', short_output=True)['metrics']
    current_revenue = finance_metrics[0]['value']
    current_works_revenue = finance_metrics[1]['value']
    current_spare_parts_revenue = finance_metrics[3]['value']

    normal_hours_metrics = stats_obj.getMetrics('normal_hours', short_output=True)['metrics']
    current_normal_hours = normal_hours_metrics[0]['value']

    metrics = [
        {
            'id': 'revenue',
            'title': 'Выручка', 
            'plan_value': plan.revenue, 
            'current_value': current_revenue,
            'metric_unit': '₽',
        },
        {
            'id': 'works_revenue',
            'title': 'Выручка с работ', 
            'plan_value': plan.works_revenue, 
            'current_value': current_works_revenue,
            'metric_unit': '₽',
        },
        {
            'id': 'spare_parts_revenue',
            'title': 'Выручка с з/ч', 
            'plan_value': plan.spare_parts_revenue, 
            'current_value': current_spare_parts_revenue,
            'metric_unit': '₽',
        },
        {
            'id': 'normal_hours',
            'title': 'Нормо-часы', 
            'plan_value': plan.normal_hours, 
            'current_value': current_normal_hours,
            'metric_unit': 'ч.',
        },
    ]

    return metrics