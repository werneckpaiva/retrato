from django.conf.urls import patterns, url
from fotos.albuns import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^album/(?P<album_name>.*)$', views.AlbumView.as_view(), name='album'),
)
