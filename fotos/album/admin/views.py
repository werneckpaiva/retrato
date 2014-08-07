from fotos.album.views import AlbumView
from django.conf import settings
from django.http import HttpResponse
import json


class AlbumAdminView(AlbumView):

    def get_context_data(self, **kwargs):
        album = self.object
        context = super(AlbumAdminView, self).get_context_data(**kwargs)
        context['visibility'] = album.get_visibility()
        self._get_pictures_visibility(context)
        return context

    # @override
    def get_album_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _get_pictures_visibility(self, context):
        album = self.object
        for picture in context["pictures"]:
            picture["visibility"] = album.get_photo_visibility(picture["filename"])

    def post(self, request, *args, **kwargs):
        album = self.get_object()
        context = {
            'album': '/%s' % self.kwargs['album_path']
        }

        visibility = request.POST.get('visibility', None)
        if visibility:
            try:
                album.set_visibility(visibility)
                context['visibility'] = album.get_visibility()
            except Exception:
                pass

        return HttpResponse(json.dumps(context), content_type="application/json")
