from django.conf.urls import patterns, url
from fotos.album import views
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^/data/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album_data'),
    url(r'^/', TemplateView.as_view(template_name='album.html'), name="album_home"),
)
