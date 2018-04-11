from django.urls import re_path, path
from django.contrib.admin.views.decorators import staff_member_required

from retrato.gdrive.admin.album.views import GdriveAlbumAdminView, GdriveAlbumAdminHomeView

urlpatterns = [
    re_path('^api/(?P<album_path>.*)$', staff_member_required(GdriveAlbumAdminView.as_view()), name='gdrive_admin_album_api'),
    re_path('^(?P<album_path>.*)$', staff_member_required(GdriveAlbumAdminHomeView.as_view()), name='gdrive_admin_album_home'),
]
