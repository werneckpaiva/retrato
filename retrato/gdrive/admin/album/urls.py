from django.urls import re_path, path
from django.views.generic.base import TemplateView
from django.contrib.admin.views.decorators import staff_member_required

from retrato.gdrive.admin.album.views import GdriveAlbumAdminView

urlpatterns = [
    re_path('^api/(?P<album_path>.*)$', staff_member_required(GdriveAlbumAdminView.as_view()), name='gdrive_admin_album_api'),
    path('', staff_member_required(TemplateView.as_view(template_name='album_admin.html')), name="gdrive_admin_album_home"),
]
