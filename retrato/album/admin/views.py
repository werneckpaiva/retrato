from django.conf import settings
from django.http import HttpResponse
import json
import logging
from retrato.album.views import AlbumView
from retrato.album.models import Album


class AlbumCacheManager():

    def purge_album_cache(self, album_path):
        from django.core.urlresolvers import reverse
        from django.http import HttpRequest
        from django.utils.cache import get_cache_key
        from django.core.cache import cache

        request = HttpRequest()
        request.path = reverse('album_data', kwargs={'album_path': album_path})
        key = get_cache_key(request)
        if key:
            if cache.get(key):
                print "Purge cache '%s'" % request.path
                cache.set(key, None, 0)


class AlbumAdminView(AlbumView, AlbumCacheManager):

    def get_context_data(self, **kwargs):
        album = self.object
        context = super(AlbumAdminView, self).get_context_data(**kwargs)
        context['visibility'] = album.get_visibility()
        self._get_pictures_visibility(context)
        return context

    # @override
    def get_album_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

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
            except Exception:
                pass
        self.purge_albunm_cache_recursively(album.path)
        return HttpResponse(json.dumps(context), content_type="application/json")

    def purge_albunm_cache_recursively(self, album_path):
        parts = album_path.split("/")
        partial_path = ''
        parts.insert(0, '')
        for path in parts:
            partial_path = Album.sanitize_path(partial_path + '/%s' % path)
            partial_path = partial_path.strip("/")
            self.purge_album_cache(partial_path)
