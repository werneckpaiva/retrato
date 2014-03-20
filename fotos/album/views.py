from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
import json
from django.views.generic.base import View
from fotos.album.models import Album
import time
import os


class AlbumView(View):

    def get(self, request, album_path=''):
        root_folder = self._get_root_folder()

        self.album = Album(root_folder, album_path)
        content = {
            'album': '/%s' % album_path,
            'pictures': self._load_pictures(),
            'albuns': self._load_albuns()
        }
        return HttpResponse(json.dumps(content), content_type="application/json")

    def _get_root_folder(self):
        if getattr(settings, 'USE_ADMIN', False):
            BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
            root_folder = os.path.join(BASE_CACHE_DIR, "album")
        else:
            root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _load_pictures(self):
        pictures = self.album.get_pictures()
        data = []
        for p in pictures:
            p.load_image_data()
            p.close_image()
            url = self._get_photo_url(p)
            data.append({'name': p.name,
                     'filename':p.filename,
                     'width':p.width,
                     'height':p.height,
                     'ratio': round(float(p.width) / float(p.height), 3),
                     'date': time.strftime('%Y-%m-%d %H:%M:%S', p.date_taken),
                     'url': url,
                     'thumb': ("%s?size=640" % url),
                     'highlight': ("%s?size=1440" % url)})
        return data

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('photo', args=(relative_url,))
        return url

    def _load_albuns(self):
        return self.album.get_albuns()
