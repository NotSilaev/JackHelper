from django.template.response import TemplateResponse


def plans(request):
    return TemplateResponse(request, 'plans/plans.html')