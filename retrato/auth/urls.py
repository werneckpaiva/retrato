from django.urls import path
from retrato.auth.views import LoginView
from django.views.generic.base import TemplateView


urlpatterns = [
    path(r'^user', TemplateView.as_view(template_name="user.html")),
    path(r'^login$', LoginView.as_view(), name='auth_login'),
    path(r'^logout$', 'django.contrib.auth.views.logout', name='auth_logout')
]
