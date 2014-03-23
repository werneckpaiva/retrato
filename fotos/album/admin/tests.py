from django.test import TestCase
from django.conf import settings
import json
import os
from shutil import rmtree
from fotos.album.models import Album


class TestAlbumAdminAcceptance(TestCase):

    def test_load_admin_page(self):
        response = self.client.get('/admin/album/')
        self.assertEqual(response.status_code, 200)

    def test_load_default_album(self):
        response = self.client.get('/admin/album/api/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/')
        self.assertEquals(len(content['albuns']), 2)
        self.assertEquals(content['pictures'], [])

    def test_make_album_public(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album1")

        if os.path.isdir(album_folder):
            os.rmdir(album_folder)

        response = self.client.post('/admin/album/api/album1/', {'visibility': 'public'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

    def test_make_album_public_with_photos(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        if os.path.isdir(album_folder):
            rmtree(album_folder)

        response = self.client.post('/admin/album/api/album2/', {'visibility': 'public'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))
        items = os.listdir(album_folder)
        self.assertTrue(len(items) > 0)
        photo_link = os.path.join(album_folder, items[0])
        self.assertTrue(os.path.islink(photo_link))

    def test_make_album_public_and_validate(self):
        settings.USE_ADMIN = True
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        if os.path.isdir(album_folder):
            rmtree(album_folder)

        response1 = self.client.post('/admin/album/api/album2/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response2 = self.client.get('/album/api/album2/')
        self.assertEqual(response2.status_code, 200)
        content = json.loads(response2.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/album2/')
        self.assertEquals(len(content['albuns']), 0)
        self.assertEquals(len(content['pictures']), 4)
        self.assertEquals(content['visibility'], Album.VISIBILITY_PUBLIC)

    def test_make_album_private(self):
        settings.USE_ADMIN = True
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album1")

        response1 = self.client.post('/admin/album/api/album1/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response = self.client.post('/admin/album/api/album1/', {'visibility': 'private'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.isdir(album_folder))

        response2 = self.client.get('/album/api/album1/')
        self.assertEqual(response2.status_code, 200)
        content = json.loads(response2.content)
        self.assert_(content)
        self.assertEquals(content['visibility'], Album.VISIBILITY_PRIVATE)
