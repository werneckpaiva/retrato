import json
import os
import time
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.detail import BaseDetailView
from django.http.response import Http404

from retrato.album.models import Album, AlbumNotFoundError
from retrato.album.auth import check_album_token_valid_or_user_authenticated,\
    UnauthorizedUserException
from django.shortcuts import render_to_response


logger = logging.getLogger(__name__)


def cache_album_context(context_func):
    def inner(self, **kwargs):
        from django.core.cache import cache

        key = self.kwargs['album_path']
        context = cache.get(key)
        if context:
            logger.debug("Cache hit - key: '%s'" % key)
            return context

        logger.debug("Cache miss - key: '%s'" % key)
        context = context_func(self, **kwargs)
        cache.set(key, context)
        return context

    return inner


class AlbumView(BaseDetailView):

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            check_album_token_valid_or_user_authenticated(request, album=self.object)
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except UnauthorizedUserException:
            return HttpResponse(status=401)

    def get_object(self):
        root_folder = self.get_album_base()
        try:
            album = Album(root_folder, self.kwargs['album_path'])
            return album
        except AlbumNotFoundError:
            raise Http404

    def get_album_context(self):
        album = self.object
        context = {
                   'path': '/%s' % self.kwargs['album_path'],
                   'title': self.kwargs['album_path'].replace('/', ' | '),
                   'pictures': self._load_pictures(album),
                   'albuns': self._load_albuns(album)
        }
        return context

    @cache_album_context
    def get_context_data(self, **kwargs):
        context = self.get_album_context()
        return context

    def render_to_response(self, context):
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
        return render_to_response('album.html', context)
