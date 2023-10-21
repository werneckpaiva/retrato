from unittest.mock import patch

from django.test import TestCase

from retrato.gdrive.album.models import GdriveAlbum
from retrato.gdrive.photo.models import GdrivePhoto


class TestPhotoModelIntegration(TestCase):

    @patch("googleapiclient.discovery.Resource")
    def test_create_photo(self, gdrive_service):
        album = GdriveAlbum(gdrive_service, "1234", "/category/album")
        photo = {
            "id": "111",
            "name": "photo_first.JPG",
            "imageMediaMetadata": {
                "width": 640,
                "height": 480
            },
            "webContentLink": "https://drive.google.com/uc?id=1GgdhkwIxBD4r6XOgS_DUzE1dQeVOlbd_&export=download",
            "thumbnailLink": "https://lh3.googleusercontent.com/drive-storage"
                             "/AKHj6E7aQJMV4b2tDpJx1okFF7YQVgv8tAfwLZ4R7S--xJPRbVRG9ovhxW0QW0ih__M5tYLsO2lm9Uc4_7qGlO"
                             "-Fa1eyEA4Zq_sbO0pQKYPv_g=s640"
        }
        gdrive_photo = GdrivePhoto(album, photo)

        self.assertEquals(gdrive_photo.filename, 'photo_first.JPG')
        self.assertEquals(gdrive_photo.relative_url(), 'category/album/photo_first.JPG')