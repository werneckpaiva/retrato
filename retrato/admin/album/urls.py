from django.urls import re_path, path
from django.views.generic.base import TemplateView
from retrato.admin.album.views import AlbumAdminView, AlbumAdminHomeView
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    re_path('^api/(?P<album_path>.*)$', staff_member_required(AlbumAdminView.as_view()), name='admin_album_api'),
    re_path(r'(?P<album_path>.*)$', staff_member_required(AlbumAdminHomeView.as_view()), name="album_home")
]
