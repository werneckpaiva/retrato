import json
import logging
import traceback

import sys
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.urls import reverse

from retrato.gdrive.album.views import GdriveAlbumView
from retrato.gdrive.photo.models import GdrivePhoto

logger = logging.getLogger(__name__)


class GdriveAlbumAdminView(GdriveAlbumView):

    def get_context_data(self, **kwargs):
        album = self.object
        context = super(GdriveAlbumAdminView, self).get_album_context()
        context['visibility'] = album.get_visibility()
        context['token'] = album.get_token()
        return context

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('admin_photo', args=(relative_url,))
        return url
        # 'api_url': reverse("gdrive_photo", kwargs={"photo": photo.relative_url()}),

    @staticmethod
    def _get_photo_api_url(photo: GdrivePhoto):
        relative_url = photo.relative_url()
        url = reverse('gdrive_photo', kwargs={"photo": relative_url})
        return url

    def _picture_to_json(self, photo:GdrivePhoto):
        data = super()._picture_to_json(photo)
        data["api_url"] = self._get_photo_api_url(photo)
        data["visibility"] = self.object.get_photo_visibility(photo.filename)
        return data

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
                context['token'] = album.get_token()
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
            # self.purge_album_cache_recursively(album.path)

        action = request.POST.get('action', None)
        if action == "revokeToken":
            self.revoke_token(album)
            context['token'] = album.get_token()
        return HttpResponse(json.dumps(context), content_type="application/json")

    def purge_album_cache_recursively(self, album_path):
        pass
    #     parts = album_path.split("/")
    #     partial_path = ''
    #     parts.insert(0, '')
    #     for path in parts:
    #         partial_path = Album.sanitize_path(partial_path + '/%s' % path)
    #         partial_path = partial_path.strip("/")
    #         self.purge_album_cache(partial_path)
    #

    def revoke_token(self, album):
        pass
    #     config = album.config()
    #     config['token'] = album.generate_token()
    #     album.save_config(config)

    def _load_albums(self, album):
        return album.get_albums()


class GdriveAlbumAdminHomeView(GdriveAlbumView):

    def render_to_response(self, context):
        return render_to_response('album_admin.html', context)
