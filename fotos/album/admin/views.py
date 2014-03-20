from fotos.album.views import AlbumView
from django.conf import settings


class AlbumAdminView(AlbumView):

    def _get_root_folder(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder
