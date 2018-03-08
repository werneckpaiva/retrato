from django.urls import path, include

from retrato.photo.views import PhotoView


urlpatterns = [
    path('album/', include('retrato.gdrive.album.urls')),
    path('photo/', include('retrato.gdrive.photo.urls')),
]
