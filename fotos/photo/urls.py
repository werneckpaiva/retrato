from django.conf.urls import patterns, url

from fotos.photo import views

urlpatterns = patterns('',
    url(r'^/(?P<photo>.*)$', views.PhotoView.as_view(), name='photo')
)
