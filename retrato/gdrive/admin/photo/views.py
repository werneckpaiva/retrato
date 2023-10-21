import json
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any

from django.http import HttpResponse
from django.http.response import Http404
from django.views.generic.base import View

from retrato.album.models import AlbumNotFoundError
from retrato.gdrive.album.models import GdriveAlbum
from retrato.gdrive.google_auth import create_google_service
from retrato.gdrive.photo.models import GdrivePhoto

T = TypeVar('T')


class BaseDetailPostView(ABC, View, Generic[T]):
    object: T = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.post_context_data(request)
        return HttpResponse(json.dumps(context), content_type="application/photo")

    @abstractmethod
    def get_object(self) -> T:
        pass

    @abstractmethod
    def post_context_data(self, ) -> Dict[str, Any]:
        pass


class GdrivePhotoAdminView(BaseDetailPostView[GdrivePhoto]):

    gdrive_service = create_google_service()

    def get_object(self) -> GdrivePhoto:
        photo_path = self.kwargs.get('photo', None)
        try:
            last_slash = photo_path.rindex("/")
            photo_name = photo_path[last_slash + 1:]
            album_path = photo_path[0:last_slash]
            album = GdriveAlbum.get_album_from_path(self.gdrive_service, album_path)
            photo = GdrivePhoto(album, {"name": photo_name})
            return photo
        except AlbumNotFoundError:
            raise Http404

    def post_context_data(self, request) -> Dict[str, Any]:
        visibility = request.POST.get('visibility', None)
        cover = request.POST.get('cover', None)
        photo = self.object
        photo.album.set_photo_visibility(photo.filename, visibility)
        return {"photo": photo.filename,
                "album": photo.album.path}
