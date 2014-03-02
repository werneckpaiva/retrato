from django.conf.urls import patterns, include, url
from fotos.album import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^album', include('fotos.album.urls')),
    url(r'^photo', include('fotos.photo.urls')),
)
