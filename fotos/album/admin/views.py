from django.core.urlresolvers import reverse
from fotos.album.views import AlbumView
from django.conf import settings
from django.http import HttpResponse
from fotos.album.models import Album
import json


class AlbumAdminView(AlbumView):

    def _get_root_folder(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('admin_photo', args=(relative_url,))
        return url

    def post(self, request, album_path='', *args, **kwargs):
        root_folder = self._get_root_folder()
        album = Album(root_folder, album_path)

        visibility = request.POST.get('visibility', None)
        if visibility:
            try:
                album.set_visibility(visibility)
                content = {
                   'album': '/%s' % album_path,
                   'visibility': album.get_visibility(),
                }
                return HttpResponse(json.dumps(content), content_type="application/json")
            except:
                pass
        return HttpResponse(status=410)
