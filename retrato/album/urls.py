from django.urls import re_path
from retrato.album import views

urlpatterns = [
#     url(r'^/api/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album_data'),
    re_path(r'api/(?P<album_path>.*)$', views.AlbumView.as_view(), name='album_data'),
    re_path(r'(?P<album_path>.*)$', views.AlbumHomeView.as_view(), name="album_home")
]
