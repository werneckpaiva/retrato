from django.http import Http404, QueryDict
from django.shortcuts import render_to_response, redirect

from retrato.album.models import AlbumNotFoundError
from retrato.album.views import AlbumView
from retrato.auth.models import UnauthorizedUserException, check_album_token_valid_or_user_authenticated
from retrato.gdrive.album.models import GdriveAlbum
from django.conf import settings
from retrato.gdrive.google_auth import create_google_service
import logging


logger = logging.getLogger(__name__)


def cache_call(context_func):
    def inner(self, *args, **kwargs):
        from django.core.cache import cache

        key = args
        context = cache.get(key)
        if context:
            logger.debug("Method call cache hit - key: '%s'" % key)
            return context

        logger.debug("Method call cache miss - key: '%s'" % key)
        context = context_func(self, *args, **kwargs)
        cache.set(key, context)
        return context

    return inner


class GdriveAlbumView(AlbumView):

    gdrive_service = create_google_service()

    def get_object(self):
        album_path = self.kwargs.get('album_path', None)
        try:
            album_id = self.get_album_id_from_path(album_path)
            album = GdriveAlbum(self.gdrive_service, album_id)
            return album
        except AlbumNotFoundError:
            raise Http404

    def get_album_context(self):
        album = self.object
        album.load_content()
        context = {
            'path': '/%s' % self.kwargs['album_path'],
            'title': self.kwargs['album_path'],
            'cover': '',
            'pictures': [],
            'albuns': album.get_albuns()
        }
        return context

    @cache_call
    def get_album_id_from_path(self, album_path):
        parent_id = settings.GDRIVE_ROOT_FOLDER_ID
        album_parts = album_path.split("/")
        for album_name in album_parts:
            if not album_name:
                continue
            results = self.gdrive_service.files().list(
                corpora="user",
                q="parents='%s' and name='%s'" % (parent_id, album_name),
                pageSize=1,
                spaces='drive',
                fields="files(id, name, mimeType)").execute()
            items = results.get('files', [])
            if len(items) == 0:
                raise AlbumNotFoundError()
            parent_id = items[0]["id"]
        return parent_id


class GdriveAlbumHomeView(GdriveAlbumView):

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            check_album_token_valid_or_user_authenticated(request, album=self.object)
            context = self.get_context_data(object=self.object)
            context['is_admin'] = (request.user and request.user.is_staff)
            if hasattr(settings, 'GOOGLE_ANALYTICS'):
                context['GOOGLE_ANALYTICS'] = settings.GOOGLE_ANALYTICS
            return self.render_to_response(context)
        except UnauthorizedUserException:
            url = "/login"
            q = QueryDict('next=%s' % self.request.path)
            url += "?" + q.urlencode(safe='/')
            return redirect(url)

    def render_to_response(self, context):
        return render_to_response('album.html', context)