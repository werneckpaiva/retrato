from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.conf import settings

from django.contrib import admin
# from django.contrib.auth.models import Group
admin.autodiscover()
# admin.site.unregister(Group)

urlpatterns = patterns('',
    url(r'^admin-user/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(url='/album/', permanent=True)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^album', include('retrato.album.urls')),
    url(r'^photo', include('retrato.photo.urls')),
)

if 'retrato.admin' in settings.INSTALLED_APPS:
    url(r'^admin/$', RedirectView.as_view(url='/admin/album', permanent=True)),
    urlpatterns += patterns('', url(r'^admin/album', include('retrato.admin.album.urls')))
    urlpatterns += patterns('', url(r'^admin/photo', include('retrato.admin.photo.urls')))
