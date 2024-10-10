from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect

from jackhelper.config import WHITE_LIST


def auth(request):
    return TemplateResponse(request, 'auth/auth.html')

def login(request):
    auth_data = request.GET

    user_id = int(auth_data['id'])
    if user_id not in WHITE_LIST:
        return HttpResponseForbidden('Telegram user_id is not in white list')

    request.session['user'] = {
        'user_id': user_id,
        'first_name': auth_data['first_name'],
        'last_name': auth_data['last_name'],
        'photo_url': auth_data['photo_url'],
    }
    request.session.save()

    return HttpResponse(status=204)
    



