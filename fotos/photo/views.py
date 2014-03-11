from django.http import HttpResponse
from django.views.generic.base import View
from django.http.response import Http404, HttpResponseNotModified
from fotos.photo.models import Photo
from fotos.photo.models.photo_cache import PhotoCache
import os
import time
from rfc822 import parsedate


class PhotoView(View):

    def get(self, request, photo=None):
        photo = self.get_photo(photo)

        self.check_if_exists(photo)

        cache = PhotoCache(photo)
        response304 = self.check_modified_since(request, cache)
        if response304:
            return response304

        cache.rotate_based_on_orientation()
        self.set_photo_size(request, cache)

        filename = cache.get_file()

        return self.return_file(filename)

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

    def check_if_exists(self, photo):
        if not photo or not photo.exists():
            raise Http404

    def set_photo_size(self, request, cache):
        size = request.GET.get('size', None)
        if size:
            cache.set_max_dimension(int(size))

    def check_modified_since(self, request, cache):
        modified_since_str = request.META.get("HTTP_IF_MODIFIED_SINCE", None)
        if modified_since_str:
            modified_since = time.mktime(parsedate(modified_since_str))
            file_time = time.mktime(cache.original_file_time())
            if modified_since >= file_time:
                return HttpResponseNotModified()

    def return_file(self, filename):
        with open(filename, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/jpeg")
            response['Content-Length'] = f.tell()
            response['Last-Modified'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(os.path.getmtime(filename)))
            return response
