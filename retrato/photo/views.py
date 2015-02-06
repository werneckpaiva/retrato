from django.conf import settings
from django.http import HttpResponse
from django.http.response import Http404, HttpResponseNotModified
from django.views.generic.detail import BaseDetailView
from retrato.photo.models import Photo
from retrato.photo.models.photo_cache import PhotoCache
import os
import time
from rfc822 import parsedate


class PhotoView(BaseDetailView):

    def get_object(self):
        photo_path = self.kwargs['photo']
        photo = None
        if photo_path:
            parts = photo_path.split('/')
            if len(parts) == 1:
                album = ''
                filename = parts[0]
            else:
                album = '/'.join(parts[:-1])
                filename = parts[-1]
            photo = Photo(self.get_photo_base(), album, filename)
        if not photo or not photo.exists():
            raise Http404
        return photo

    def render_to_response(self, context):
        photo = self.object
        cache = PhotoCache(photo)
        response304 = self.check_modified_since(cache)
        if response304:
            return response304
        cache.rotate_based_on_orientation()

        size = self.request.GET.get('size', None)
        if size:
            cache.set_max_dimension(int(size))
            filename = cache.get_file()
        else:
            filename = cache.get_original_file()

        return self.output_file(filename, photo.filename)

    def get_photo_base(self):
        if 'retrato.admin' not in settings.INSTALLED_APPS:
            root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        else:
            BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
            root_folder = os.path.join(BASE_CACHE_DIR, "album")
        return root_folder

    def check_modified_since(self, cache):
        modified_since_str = self.request.META.get("HTTP_IF_MODIFIED_SINCE", None)
        if modified_since_str:
            modified_since = time.mktime(parsedate(modified_since_str))
            file_time = time.mktime(cache.original_file_time())
            if modified_since >= file_time:
                return HttpResponseNotModified()

    def output_file(self, filename, original_filename):
        with open(filename, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/jpeg")
            response['Content-Length'] = f.tell()
            response['Last-Modified'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(os.path.getmtime(filename)))
            response['Cache-Control'] = 'public, max-age=9999999'
            if self.request.GET.get('download', None) is not None:
                response['Content-disposition'] = 'attachment; filename=%s' % (original_filename)
            return response
