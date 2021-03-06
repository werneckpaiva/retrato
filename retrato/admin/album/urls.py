from django.urls import re_path, path
from django.views.generic.base import TemplateView
from retrato.admin.album.views import AlbumAdminView
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    re_path('^api/(?P<album_path>.*)$', staff_member_required(AlbumAdminView.as_view()), name='admin_album_api'),
    path('', staff_member_required(TemplateView.as_view(template_name='album_admin.html')), name="admin_album_home"),
]
