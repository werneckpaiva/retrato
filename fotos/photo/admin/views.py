from django.conf import settings
from fotos.photo.views import PhotoView


class PhotoAdminView(PhotoView):

    def get_photo_base(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        return root_folder
