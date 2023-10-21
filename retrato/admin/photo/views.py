from django.conf import settings
from retrato.photo.views import PhotoView
from django.http import HttpResponse
import json
from retrato.album.models import Album
from retrato.admin.album.views import AlbumCacheManager
from django.http.response import Http404


class PhotoAdminView(PhotoView, AlbumCacheManager):

    # @override
    def get_photo_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = {
            'photo': '/%s' % self.kwargs['photo']
        }

        visibility = request.POST.get('visibility', None)
        cover = request.POST.get('cover', None)

        if visibility is not None:
            partial_context = self._change_photo_visibility(visibility)
            context.update(partial_context)
        elif cover is not None:
            partial_context = self._set_album_cover()
            context.update(partial_context)
        else:
            raise Http404()

        return HttpResponse(json.dumps(context), content_type="application/photo")

    def _change_photo_visibility(self, visibility):
        photo = self.object
        context = {}
        album = Album(settings.PHOTOS_ROOT_DIR, photo.album)
        album.set_photo_visibility(photo.filename, visibility)
        context['visibility'] = album.get_photo_visibility(photo.filename)
        self.purge_album_cache(photo.album)
        return context

    def _set_album_cover(self):
        photo = self.object
        context = {}
        album = Album(settings.PHOTOS_ROOT_DIR, photo.album)
        album.set_cover(photo.filename)
        self.purge_album_cache(photo.album)
        return context
