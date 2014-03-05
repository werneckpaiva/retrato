from django.conf.urls import patterns, include, url
from fotos.album import views
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/album/', permanent=True)),
    url(r'^album/', views.index, name='home'),
    url(r'^album-data', include('fotos.album.urls')),
    url(r'^photo', include('fotos.photo.urls')),
    url(r'^jasmine/', include('django_jasmine.urls')),
)
