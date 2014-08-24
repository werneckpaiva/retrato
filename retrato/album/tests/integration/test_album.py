from django.test import TestCase
from django.conf import settings
from retrato.album.models import Album


class TestAlbumModelIntegration(TestCase):

    def test_create_album(self):
        PHOTOS_ROOT_DIR = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        album = Album(PHOTOS_ROOT_DIR, '/')
        self.assertEquals(album.get_pictures(), [])
        self.assertEquals(len(album.get_albuns()), 2)

    def test_sanitize_path__remove_first_slash(self):
        path = "/album"
        sanitized_path = Album.sanitize_path(path)
        self.assertEquals(sanitized_path, 'album')

    def test_sanitize_path__remove_dot_dot(self):
        path = "/../album"
        sanitized_path = Album.sanitize_path(path)
        self.assertEquals(sanitized_path, 'album')

    def test_sanitize_path__remove_two_slashes(self):
        path = "album1//album2"
        sanitized_path = Album.sanitize_path(path)
        self.assertEquals(sanitized_path, 'album1/album2')

    def test_sanitize_path__potentially_attack1(self):
        path = "/etc/"
        sanitized_path = Album.sanitize_path(path)
        self.assertEquals(sanitized_path, 'etc/')

    def test_sanitize_path__potentially_attack2(self):
        path = "../../../etc/"
        sanitized_path = Album.sanitize_path(path)
        self.assertEquals(sanitized_path, 'etc/')
