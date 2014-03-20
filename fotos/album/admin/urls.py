from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from fotos.album.admin.views import AlbumAdminView


urlpatterns = patterns('',
    url(r'^/data/(?P<album_path>.*)$', AlbumAdminView.as_view(), name='admin_album_data'),
    url(r'^/', TemplateView.as_view(template_name='admin/album_admin.html'), name="admin_album_home"),
)
