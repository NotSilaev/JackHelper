from django.template.response import TemplateResponse


def stats(request):
    return TemplateResponse(request, 'stats/stats.html')