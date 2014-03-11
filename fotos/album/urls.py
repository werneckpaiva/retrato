from django.conf.urls import patterns, url
from fotos.album import views
from django.views.decorators.cache import cache_page


urlpatterns = patterns('',
    url(r'^/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album')
)
