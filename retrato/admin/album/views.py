import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from retrato.album.views import AlbumView
from retrato.album.models import Album


logger = logging.getLogger(__name__)


class AlbumCacheManager():

    def purge_album_cache(self, album_path):
        from django.core.cache import cache
        key = album_path
        if cache.get(album_path):
            logger.debug("Purge cache '%s'" % key)
            cache.set(key, None, 0)


class AlbumAdminView(AlbumView, AlbumCacheManager):

    def get_context_data(self, **kwargs):
        album = self.object
        context = super(AlbumAdminView, self).get_album_context()
        context['visibility'] = album.get_visibility()
        context['token'] = album.get_token()
        self._get_pictures_visibility(context)
        return context

    # @override
    def get_album_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('admin_photo', args=(relative_url,))
        return url

    def _get_pictures_visibility(self, context):
        album = self.object
        for picture in context["pictures"]:
            picture["visibility"] = album.get_photo_visibility(picture["filename"])

    def post(self, request, *args, **kwargs):
        album = self.get_object()
        context = {
            'album': '/%s' % self.kwargs['album_path']
        }

        visibility = request.POST.get('visibility', None)
        if visibility:
            try:
                album.set_visibility(visibility)
                context['visibility'] = album.get_visibility()
                context['token'] = album.get_token()
            except Exception:
                pass
        self.purge_album_cache_recursively(album.path)
        return HttpResponse(json.dumps(context), content_type="application/json")

    def purge_album_cache_recursively(self, album_path):
        parts = album_path.split("/")
        partial_path = ''
        parts.insert(0, '')
        for path in parts:
            partial_path = Album.sanitize_path(partial_path + '/%s' % path)
            partial_path = partial_path.strip("/")
            self.purge_album_cache(partial_path)
