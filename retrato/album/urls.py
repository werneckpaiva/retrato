from django.urls import re_path
from retrato.album import views

urlpatterns = [
    re_path(r'api/(?P<album_path>.*)$', views.AlbumView.as_view(), name='album_data'),
    re_path(r'(?P<album_path>.*)$', views.AlbumHomeView.as_view(), name="album_home")
]
