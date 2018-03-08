from django.urls import path

from retrato.gdrive.photo.views import GdrivePhotoView


urlpatterns = [path('<path:photo>', GdrivePhotoView.as_view(), name='gdrive_photo')]
