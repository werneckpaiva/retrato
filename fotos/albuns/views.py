from django.template import Context, loader
from django.http import HttpResponse
import json
import django
from django.views.generic.base import View


def index(request):
    t = loader.get_template('albuns/index.html')
    c = Context({
        'version': django.get_version()
    })
    return HttpResponse(t.render(c))


class AlbumView(View):

    def get(self, request, album_name=''):
        content = {
            'album': '/%s' % album_name
        }
        return HttpResponse(json.dumps(content), content_type="application/json")

    def _load_pictures(self):
        