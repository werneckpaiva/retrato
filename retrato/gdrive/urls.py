from django.conf import settings
from django.views.generic import RedirectView
from django.urls import re_path, path, include

urlpatterns = [
    path('album/', include('retrato.gdrive.album.urls')),
    path('photo/', include('retrato.gdrive.photo.urls')),
]

if 'retrato.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += [
        path('admin/', RedirectView.as_view(url='/gdrive/admin/album', permanent=True)),
        path('admin/album/', include('retrato.gdrive.admin.album.urls')),
        path('admin/photo/', include('retrato.gdrive.admin.photo.urls'))
    ]