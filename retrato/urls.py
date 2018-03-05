from django.urls import path, re_path, include
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/album/', permanent=True)),
    path('album/', include('retrato.album.urls')),
    path('photo/', include('retrato.photo.urls')),
]

if 'retrato.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += [
        path('_admin/', admin.site.urls),
        re_path('^admin/$', RedirectView.as_view(url='/admin/album', permanent=True)),
        path('admin/album/', include('retrato.admin.album.urls')),
        path('admin/photo/', include('retrato.admin.photo.urls'))
    ]

if settings.REQUIRE_AUTHENTICATION:
    urlpatterns += [path('', include('retrato.auth.urls'))]