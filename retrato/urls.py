from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.conf import settings

# from django.contrib.auth.models import Group
# admin.site.unregister(Group)

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/album/', permanent=True)),
    url(r'^album', include('retrato.album.urls')),
    url(r'^photo', include('retrato.photo.urls')),
)

if 'retrato.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += patterns('',
        url(r'^_admin/', include(admin.site.urls)),
        url(r'^admin/$', RedirectView.as_view(url='/admin/album', permanent=True)),
        url(r'^admin/album', include('retrato.admin.album.urls')),
        url(r'^admin/photo', include('retrato.admin.photo.urls'))
    )

if settings.REQUIRE_AUTHENTICATION:
    urlpatterns += patterns('',
        url(r'', include('retrato.auth.urls'))
    )
