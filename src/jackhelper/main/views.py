from django.template.response import TemplateResponse


def main(request):
    return TemplateResponse(request, 'main/main.html')


def custom_404(request, exception):
    return TemplateResponse(request, 'errors/404.html', status=404)