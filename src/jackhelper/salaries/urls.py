from django.urls import path

from .views import *
from .api import *


urlpatterns = [
    path('', salaries, name='salaries'),
    path('download_salaries_file/<str:filename>/', downloadSalariesFile, name='download_salaries_file'),

    path('api/getSalariesBlock/', getSalariesBlock, name='get_salaries_block'),
    path('api/addSalaryMetric/', addSalaryMetric, name='add_salary_metric'),
    path('api/removeSalaryMetric/', removeSalaryMetric, name='remove_salary_metric'),
    path(
        'api/getSalariesExcelFileDownloadURL/', 
        getSalariesExcelFileDownloadURL, 
        name='get_salaries_excel_file_donwload_url'
    ),
]