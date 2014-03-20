from django.core.urlresolvers import reverse
from fotos.album.views import AlbumView
from django.conf import settings


class AlbumAdminView(AlbumView):

    def _get_root_folder(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder

    def _get_photo_url(self, photo):
        relative_url = photo.relative_url()
        url = reverse('admin_photo', args=(relative_url,))
        return url
