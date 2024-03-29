import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from retrato.album.views import AlbumView
from retrato.album.models import Album
from retrato.photo.models import Photo
from django.shortcuts import render_to_response

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

    def _get_photo_url(self, photo: Photo):
        return reverse('admin_photo', args=(photo.relative_url(),))

    def _get_photo_api_url(self, photo: Photo):
        return self._get_photo_url(photo)

    def _picture_to_json(self, photo):
        data = super()._picture_to_json(photo)
        data["api_url"] = self._get_photo_api_url(photo)
        return data

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
                album.make_all_photos_public()
                context['visibility'] = album.get_visibility()
                context['token'] = album.get_token()
            except:
                pass
            self.purge_album_cache_recursively(album.path)

        action = request.POST.get('action', None)
        if action == "revokeToken":
            self.revoke_token(album)
            context['token'] = album.get_token()
        return HttpResponse(json.dumps(context), content_type="application/json")

    def purge_album_cache_recursively(self, album_path):
        parts = album_path.split("/")
        partial_path = ''
        parts.insert(0, '')
        for path in parts:
            partial_path = Album.sanitize_path(partial_path + '/%s' % path)
            partial_path = partial_path.strip("/")
            self.purge_album_cache(partial_path)

    def revoke_token(self, album):
        config = album.config()
        config['token'] = album.generate_token()
        album.save_config(config)


class AlbumAdminHomeView(AlbumView):

    def render_to_response(self, context):
        return render_to_response('album_admin.html', context)
