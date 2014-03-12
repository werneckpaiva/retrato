from django.template import Context, loader
from django.http import HttpResponse
import json
import django
from django.views.generic.base import View
from fotos.album.models import Album
import time


def index(request):
    t = loader.get_template('album/index.html')
    c = Context({
        'version': django.get_version()
    })
    return HttpResponse(t.render(c))


class AlbumView(View):

    def get(self, request, album_path=''):
        self.album = Album(album_path)
        content = {
            'album': '/%s' % album_path,
            'pictures': self._load_pictures(),
            'albuns': self._load_albuns()
        }
        return HttpResponse(json.dumps(content), content_type="application/json")

    def _load_pictures(self):
        pictures = self.album.get_pictures()
        for p in pictures:
            p.load_image_data()
            p.close_image()
        data = [{'name': p.name,
                     'filename':p.filename,
                     'width':p.width,
                     'height':p.height,
                     'ratio': round(float(p.width) / float(p.height), 3),
                     'date': time.strftime('%Y-%m-%d %H:%M:%S', p.date_taken),
                     'url': p.url,
                     'thumb': ("%s?size=640" % p.url),
                     'highlight': ("%s?size=1440" % p.url)} \
                   for p in pictures]
        return data

    def _load_albuns(self):
        return self.album.get_albuns()
