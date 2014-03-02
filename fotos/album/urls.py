from django.conf.urls import patterns, url
from fotos.album import views


urlpatterns = patterns('',
    url(r'^/(?P<album_path>.*)$', views.AlbumView.as_view(), name='album')
)
