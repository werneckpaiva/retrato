from django.test import TestCase
from fotos.album.models import Photo


class TestPhotoModelIntegration(TestCase):

    def test_create_photo(self):
        photo = Photo("album2", 'photo_first.JPG')
        self.assertEquals(photo.filename, 'photo_first.JPG')
        self.assertEquals(photo.name, 'photo first')
        self.assertTrue(photo.exists())
        self.assertEquals(photo.url, '/photo/album2/photo_first.JPG')
