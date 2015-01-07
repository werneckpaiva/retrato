from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.conf import settings
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login


class LoginException(Exception):
    code = None
    message = None

    def __init__(self, code, message):
        super(LoginException, self).__init__(message)
        self.code = code
        self.message = message


class LoginView(View):

    def get(self, request, *args, **kwargs):
        context = {
            'FACEBOOK_ID': settings.FACEBOOK_ID,
            'REDIRECT_TO': request.GET.get('next', None)
        }
        return render_to_response('login.html', context)

    def post(self, request, *args, **kwargs):
        facebookAccessToken = request.POST.get('accessToken')
        facebookUserID = request.POST.get('userID')
#         expires = request.POST.get('expires')
        user = authenticate(facebookUserID=facebookUserID, facebookAccessToken=facebookAccessToken)
        try:
            if user is not None and user.is_active:
                login(request, user)
                if user.is_authenticated():
                    context = {'success': True,
                               'first_name': user.first_name,
                               'last_name': user.last_name}
                else:
                    raise LoginException('NOT_AUTHORIZED_PERIOD_EXPIRED', 'Allowed period expired.')
            else:
                raise LoginException('LOGIN_FAILED', 'Login failed')
        except LoginException as e:
            context = {'success': False,
                       'status': e.code,
                       'message': e.message}
        response = HttpResponse(json.dumps(context), content_type="application/json")
        return response
