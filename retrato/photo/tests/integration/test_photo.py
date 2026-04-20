from django.test import TestCase
from django.conf import settings
from retrato.photo.models import Photo


class TestPhotoModelIntegration(TestCase):

    def test_create_photo(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')

        self.assertEqual(photo.filename, 'photo_first.JPG')

        photo.load_name()
        self.assertEqual(photo.name, 'photo first')

        self.assertTrue(photo.exists())

        self.assertEqual(photo.relative_url(), 'album2/photo_first.JPG')
