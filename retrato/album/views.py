import json
import os
import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView
from django.http.response import Http404, HttpResponseForbidden

from retrato.album.models import Album, AlbumNotFoundError
from retrato.album.auth import check_album_token_valid_or_user_authenticated,\
    UnauthorizedUserException, redirect_to_login
from django.shortcuts import render, render_to_response


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
        try:
            check_album_token_valid_or_user_authenticated(self.request, album=self.object)
        except UnauthorizedUserException:
            return HttpResponse(status=401)
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
            ratio = round(float(p.width) / float(p.height), 3)
            data.append({'name': p.name,
                     'filename': p.filename,
                     'width': p.width,
                     'height': p.height,
                     'ratio': ratio,
                     'date': time.strftime('%Y-%m-%d %H:%M:%S', p.date_taken),
                     'url': url,
                     'thumb': ("%s?size=640" % url),
                     'thumb_width': (640 if p.width >= p.height else (640 * ratio)),
                     'thumb_height': (640 if p.height > p.width else (640 / ratio)),
                     'highlight': ("%s?size=1440" % url)})
        return data

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('photo', args=(relative_url,))
        return url

    def _load_albuns(self, album):
        return album.get_albuns()


class AlbumHomeView(AlbumView):

    def render_to_response(self, context):
        try:
            check_album_token_valid_or_user_authenticated(self.request, album=self.object)
        except UnauthorizedUserException:
#             return redirect_to_login(self.request)
            return HttpResponse(status=401)
        return render_to_response('album.html', context)
