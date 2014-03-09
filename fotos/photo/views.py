from django.http import HttpResponse
from django.views.generic.base import View
from django.http.response import Http404
from fotos.photo.models import Photo


class PhotoView(View):

    def get(self, request, photo=None):
        p = self.get_photo(photo)
        if not p or not p.exists():
            raise Http404
        response = p.save_to_response(HttpResponse(content_type="image/jpeg"))
        return response

    def get_photo(self, photo):
        if not photo:
            return None
        parts = photo.split('/')
        if len(parts) == 1:
            return Photo('', parts[0])
        else:
            album = '/'.join(parts[:-1])
            filename = parts[-1]
            return Photo(album, filename)
