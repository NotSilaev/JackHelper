from django.http import HttpResponse, JsonResponse

from .models import SalaryMetric
from .salaries import *
from .salaries_excel import makeSalariesExcelFile


def getSalariesBlock(request):
    block_id = request.GET.get('block_id')
    city = request.GET.get('city')
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))

    salaries_block = Salaries(city, year, month).getBlockData(block_id)
    
    return JsonResponse(salaries_block, status=200)


def addSalaryMetric(request):
    fullname = request.POST.get('fullname')
    city = request.POST.get('city')
    year = request.POST.get('year')
    month = request.POST.get('month')
    metric_amount = int(request.POST.get('metric_amount'))
    metric_comment = request.POST.get('metric_comment')
    metric_type = request.POST.get('metric_type')

    if metric_amount > 1_000_000:
        return JsonResponse({'errors': [{'text': 'Слишком большая сумма'}]}, status=400)
    if len(metric_comment) > 200:
        return JsonResponse({'errors': [{'text': 'Слишком длинный комментарий'}]}, status=400)

    SalaryMetric.objects.create(
        employee=fullname,
        city=city,
        year=year,
        month=month,
        metric_amount=metric_amount,
        metric_comment=metric_comment,
        metric_type=metric_type,
    )

    return HttpResponse(status=201)


def removeSalaryMetric(request):
    metric_id = request.POST.get('metric_id')

    try:
        SalaryMetric.objects.get(id=metric_id).delete()
    except SalaryMetric.DoesNotExist:
        raise ValueError('Metric not found')
        
    return HttpResponse(status=201)


def getSalariesExcelFileDownloadURL(request):
    city = request.GET.get('city')
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))

    salaries_blocks = Salaries(city, year, month).getAllBlocksData()

    salaries_data = {
        'city': city,
        'year': year,
        'month': month,
        'salaries_blocks': salaries_blocks,
    }
    filename = makeSalariesExcelFile(salaries_data)
    
    download_url = f'download_salaries_file/{filename}'
    return JsonResponse({'download_url': download_url}, status=200)