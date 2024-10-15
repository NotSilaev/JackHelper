from django.urls import path

from .views import *
from .api import *


urlpatterns = [
    path('', plans, name='plans'),

    path('api/getAvailableMonths/', getAvailableMonths, name='get_available_months'),
    path('api/getPlanMetrics/', getPlanMetrics, name='get_plan_metrics'),
    path('api/setMonthPlan/', setMonthPlan, name='set_month_plan'),
]