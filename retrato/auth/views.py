from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.conf import settings
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login


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
        if user is not None and user.is_active:
            login(request, user)
            if user.is_authenticated():
                context = {'success': True,
                           'first_name': user.first_name,
                           'last_name': user.last_name}
            else:
                context = {'success': False, 'status': 'NOT_AUTHORIZED_PERIOD_EXPIRED'}
        else:
            context = {'success': False, 'status': 'LOGIN_FAILED'}
        response = HttpResponse(json.dumps(context), content_type="application/json")
        return response