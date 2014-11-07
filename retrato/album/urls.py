from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from retrato.album import views
from retrato.album.auth import login_or_token_required
from django.conf import settings

urlpatterns = patterns('',
    url(r'^/api/(?P<album_path>.*)$', cache_page(60 * 60 * 24 * 5)(views.AlbumView.as_view()), name='album_data'),
)

if getattr(settings, 'REQUIRE_AUTHENTICATION', False):
    urlpatterns += patterns('', url(r'^/', login_or_token_required(TemplateView.as_view(template_name='album.html')), name="album_home"))
else:
    urlpatterns += patterns('', url(r'^/', TemplateView.as_view(template_name='album.html'), name="album_home"))
