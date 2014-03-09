from django.test import TestCase
from fotos.photo.models import Photo


class TestPhotoModelIntegration(TestCase):

    def test_create_photo(self):
        photo = Photo("album2", 'photo_first.JPG')

        self.assertEquals(photo.filename, 'photo_first.JPG')

        photo.load_name()
        self.assertEquals(photo.name, 'photo first')

        self.assertTrue(photo.exists())

        photo.load_url()
        self.assertEquals(photo.url, '/photo/album2/photo_first.JPG')
