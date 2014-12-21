from django.conf.urls import patterns, url
from retrato.album import views

urlpatterns = patterns('',
#     url(r'^/api/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album_data'),
    url(r'^/api/(?P<album_path>.*)$', views.AlbumView.as_view(), name='album_data'),
    url(r'^/(?P<album_path>.*)$', views.AlbumHomeView.as_view(), name="album_home")
)
