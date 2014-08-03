from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

# from django.contrib import admin
# from django.contrib.auth.models import Group
# admin.autodiscover()
# admin.site.unregister(Group)

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/album/', permanent=True)),
    url(r'^admin/$', RedirectView.as_view(url='/admin/album', permanent=True)),
    url(r'^album', include('fotos.album.urls')),
    url(r'^photo', include('fotos.photo.urls')),

    url(r'^admin/album', include('fotos.album.admin.urls')),
    url(r'^admin/photo', include('fotos.photo.admin.urls')),

    url(r'^jasmine/', include('django_jasmine.urls')),
)
