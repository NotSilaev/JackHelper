from django.template.response import TemplateResponse


def orders(request):
    return TemplateResponse(request, 'orders/orders.html')