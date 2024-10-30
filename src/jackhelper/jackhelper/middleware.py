from django.http import HttpResponse, JsonResponse
from django.conf import settings

from . import logs

import traceback


class ExceptionMiddleware:
    def __init__(self, next):
        self.next = next

    def __call__(self, request):
        response = self.next(request)
        return response

    def process_exception(self, request, exception):
        logs.addLog(level='error', text=traceback.format_exc(), send_telegram_message=True)

        if settings.DEBUG:
            return JsonResponse({'errors': [{'text': str(exception)}]}, status=500)
        else:
            return JsonResponse({'errors': [{'text': 'Произошла неизвестная ошибка'}]}, status=500)