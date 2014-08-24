from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.conf import settings

# from django.contrib import admin
# from django.contrib.auth.models import Group
# admin.autodiscover()
# admin.site.unregister(Group)

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/album/', permanent=True)),
    url(r'^admin/$', RedirectView.as_view(url='/admin/album', permanent=True)),
    url(r'^album', include('retrato.album.urls')),
    url(r'^photo', include('retrato.photo.urls')),

    url(r'^admin/album', include('retrato.admin.album.urls')),
    url(r'^admin/photo', include('retrato.admin.phpto.urls')),
)

if 'django_jasmine' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^jasmine/', include('django_jasmine.urls')))
