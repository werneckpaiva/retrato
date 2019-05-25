from django.urls import include, re_path
from retrato.auth.views import LoginView
from django.views.generic.base import TemplateView


urlpatterns = [
    re_path(r'^user', TemplateView.as_view(template_name="user.html")),
    re_path(r'^login$', LoginView.as_view(), name='auth_login'),
    # path(r'^logout$', include('django.contrib.auth.logout'), name='auth_logout')
]
