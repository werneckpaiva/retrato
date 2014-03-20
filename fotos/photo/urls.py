from django.conf.urls import patterns, url
from fotos.photo.views import PhotoView


urlpatterns = patterns('',
    url(r'^/(?P<photo>.*)$', PhotoView.as_view(), name='photo')
)
