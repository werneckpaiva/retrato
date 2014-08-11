from django.conf import settings
from fotos.photo.views import PhotoView
from django.http import HttpResponse
import json
from fotos.album.models import Album


class PhotoAdminView(PhotoView):

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
                cache.set(key, None, 0)