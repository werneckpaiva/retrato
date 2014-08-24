from django.conf import settings
from retrato.photo.views import PhotoView
from django.http import HttpResponse
import json
from retrato.album.models import Album
from retrato.album.admin.views import AlbumCacheManager


class PhotoAdminView(PhotoView, AlbumCacheManager):

    # @override
    def get_photo_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def post(self, request, *args, **kwargs):
        photo = self.get_object()
        context = {
            'photo': '/%s' % self.kwargs['photo']
        }

        visibility = request.POST.get('visibility', None)
        if visibility:
            album = Album(settings.PHOTOS_ROOT_DIR, photo.album)
            album.set_photo_visibility(photo.filename, visibility)
            context['visibility'] = album.get_photo_visibility(photo.filename)

            self.purge_album_cache(photo.album)

        return HttpResponse(json.dumps(context), content_type="application/json")
