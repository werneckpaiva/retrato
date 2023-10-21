from django.conf import settings
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('album/', include('retrato.gdrive.album.urls')),
]

if 'retrato.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += [
        path('admin/', RedirectView.as_view(url='/admin/album', permanent=True)),
        path('admin/album/', include('retrato.gdrive.admin.album.urls')),
        path('admin/photo/', include('retrato.gdrive.admin.photo.urls'))
    ]