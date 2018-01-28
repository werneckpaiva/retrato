from django.urls import path

from retrato.photo.views import PhotoView


urlpatterns = [path('<path:photo>', PhotoView.as_view(), name='photo')]
