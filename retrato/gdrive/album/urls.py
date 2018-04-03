from django.urls import re_path


from retrato.gdrive.album.views import GdriveAlbumView, GdriveAlbumHomeView

urlpatterns = [
    re_path(r'api/(?P<album_path>.*)$', GdriveAlbumView.as_view(), name='gdrive_album_data'),
    re_path(r'(?P<album_path>.*)$', GdriveAlbumHomeView.as_view(), name="gdrive_album_home")
]
