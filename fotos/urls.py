from django.conf.urls import patterns, include, url
from fotos.albuns import views

urlpatterns = patterns('',
    url(r'^album', include('fotos.albuns.urls')),
    url(r'^photo', include('fotos.photo.urls')),
    url(r'^/$', views.index, name='home'),
)
