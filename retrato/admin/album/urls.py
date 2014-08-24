from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from retrato.admin.album.views import AlbumAdminView


urlpatterns = patterns('',
    url(r'^/api/(?P<album_path>.*)$', AlbumAdminView.as_view(), name='admin_album_api'),
    url(r'^/', TemplateView.as_view(template_name='album_admin.html'), name="admin_album_home"),
)