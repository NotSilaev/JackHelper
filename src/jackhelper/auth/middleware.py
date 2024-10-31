from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse


class AuthMiddleware:
    '''Checks the user's "sessionid" cookie before performing the requested URL view.'''

    def __init__(self, next):
        self.next = next

    def __call__(self, request):
        path = request.path
        path_root = path.split('/')[1]

        if 'user' not in request.session:
            if ('api' in path): return HttpResponse('Unauthorized', status=401)
            elif (path_root != 'auth'): return redirect(reverse('auth'))
        elif ('user' in request.session) and (path_root == 'auth'):
            return redirect(reverse('main'))

        response = self.next(request)
        return response
    