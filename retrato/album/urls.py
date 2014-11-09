from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from retrato.album import views

urlpatterns = patterns('',
    url(r'^/api/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album_data'),
    url(r'^/', views.album_home_view, name="album_home")
)
