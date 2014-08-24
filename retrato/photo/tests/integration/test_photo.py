from django.test import TestCase
from django.conf import settings
from retrato.photo.models import Photo


class TestPhotoModelIntegration(TestCase):

    def test_create_photo(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')

        self.assertEquals(photo.filename, 'photo_first.JPG')

        photo.load_name()
        self.assertEquals(photo.name, 'photo first')

        self.assertTrue(photo.exists())

        self.assertEquals(photo.relative_url(), 'album2/photo_first.JPG')
