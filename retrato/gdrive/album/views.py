import logging
from typing import Dict

from django.conf import settings
from django.http import Http404, QueryDict
from django.shortcuts import render_to_response, redirect

from retrato.album.models import AlbumNotFoundError
from retrato.album.views import AlbumView
from retrato.auth.models import UnauthorizedUserException, check_album_token_valid_or_user_authenticated
from retrato.gdrive.album.models import GdriveAlbum
from retrato.gdrive.google_auth import create_google_service
from retrato.gdrive.photo.models import GdrivePhoto

logger = logging.getLogger(__name__)


class GdriveAlbumView(AlbumView):
    gdrive_service = create_google_service()

    def get_object(self) -> GdriveAlbum:
        album_path = self.kwargs.get('album_path', None)
        try:
            album = GdriveAlbum.get_album_from_path(self.gdrive_service, album_path)
            return album
        except AlbumNotFoundError:
            raise Http404

    def get_album_context(self):
        album = self.object
        album.load_content()
        context = {
            'path': album.path,
            'title': album.title,
            'cover': '',
            'pictures': self._load_pictures(album),
            'albums': self._load_albums(album),
            'base_url': '/album/'
        }
        return context

    def _load_albums(self, album):
        return album.get_public_albums()

    def _picture_to_json(self, photo: GdrivePhoto) -> Dict[str, str | float]:
        ratio = round(photo.ratio, 3)
        data = {'name': photo.name,
                'filename': photo.filename,
                'width': photo.width,
                'height': photo.height,
                'ratio': ratio,
                'date': photo.date_taken,
                'url': photo.url,
                'download_url': photo.url,
                'thumb': photo.thumb,
                'thumb_width': round(640 if photo.width >= photo.height else (640 * ratio)),
                'thumb_height': round(640 if photo.height > photo.width else (640 / ratio)),
                'highlight': photo.highlight}
        return data


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
