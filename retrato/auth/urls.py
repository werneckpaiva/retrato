from django.conf.urls import patterns, url
from retrato.auth.views import LoginView
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
    url(r'^user', TemplateView.as_view(template_name="user.html")),
    url(r'^login$', LoginView.as_view(), name='auth_login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', name='auth_logout')
)
