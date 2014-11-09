import json
import os
import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView
from django.http.response import Http404

from retrato.album.models import Album, AlbumNotFoundError
from retrato.album.auth import check_album_token_valid_or_user_authenticated
from django.shortcuts import render


class AlbumView(BaseDetailView):

    def get_object(self):
        root_folder = self.get_album_base()
        try:
            album = Album(root_folder, self.kwargs['album_path'])
            return album
        except AlbumNotFoundError:
            raise Http404

    def get_context_data(self, **kwargs):
        album = self.object
        context = {
                   'path': '/%s' % self.kwargs['album_path'],
                   'pictures': self._load_pictures(album),
                   'albuns': self._load_albuns(album)
        }
        return context

    def render_to_response(self, context):
        response = check_album_token_valid_or_user_authenticated(self.request, album=self.object)
        if response is not None:
            return response
        return HttpResponse(json.dumps(context), content_type="application/json")

    @classmethod
    def get_album_base(cls):
        if 'retrato.admin' in settings.INSTALLED_APPS:
            BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
            root_folder = os.path.join(BASE_CACHE_DIR, "album")
        else:
            root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _load_pictures(self, album):
        pictures = album.get_pictures()
        data = []
        for p in pictures:
            p.load_image_data()
            p.close_image()
            url = self._get_photo_url(p)
            data.append({'name': p.name,
                     'filename': p.filename,
                     'width': p.width,
                     'height': p.height,
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

    def _load_albuns(self, album):
        return album.get_albuns()


def album_home_view(request):
    check_album_token_valid_or_user_authenticated(request)
    response = check_album_token_valid_or_user_authenticated(request)
    if response is not None:
        return response
    return render(request, 'album.html')
