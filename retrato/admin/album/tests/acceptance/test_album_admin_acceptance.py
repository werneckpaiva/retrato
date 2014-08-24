from django.test import TestCase
from django.conf import settings
import json
import os
from retrato.album.models import Album
from shutil import rmtree


class TestAlbumAdminAcceptance(TestCase):

    def test_load_admin_page(self):
        response = self.client.get('/admin/album/')
        self.assertEqual(response.status_code, 200)

    def test_load_default_album(self):
        response = self.client.get('/admin/album/api/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['path'], '/')
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
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        if os.path.isdir(album_folder):
            rmtree(album_folder)

        response_not_found = self.client.get('/album/api/album2/')
        self.assertEqual(response_not_found.status_code, 404)

        response1 = self.client.post('/admin/album/api/album2/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response2 = self.client.get('/album/api/album2/')
        self.assertEqual(response2.status_code, 200)
        content = json.loads(response2.content)
        self.assert_(content)
        self.assertEquals(content['path'], '/album2/')
        self.assertEquals(len(content['albuns']), 0)
        self.assertEquals(len(content['pictures']), 4)

    def test_make_album_private(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album1")

        response1 = self.client.post('/admin/album/api/album1/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response = self.client.post('/admin/album/api/album1/', {'visibility': 'private'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.isdir(album_folder))

        response2 = self.client.get('/album/api/album1/')
        self.assertEqual(response2.status_code, 404)

    def test_make_parent_album_private(self):
        new_album = 'album3/first/second/'
        
        # create album3 with subalbuns
        new_real_folder = os.path.join(settings.PHOTOS_ROOT_DIR, new_album)
        try:
            os.makedirs(new_real_folder)
        except:
            pass

        virtual_base_folder = Album.get_virtual_base_folder()
        virtual_folder = os.path.join(virtual_base_folder, new_album)

        response1 = self.client.post('/admin/album/api/%s' % new_album, {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(virtual_folder))

        response2 = self.client.post('/admin/album/api/%s' % new_album, {'visibility': 'private'})
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(os.path.isdir(virtual_folder))

        response3a = self.client.get('/album/api/album3/first/second/')
        self.assertEqual(response3a.status_code, 404)
        response3b = self.client.get('/album/api/album3/first/')
        self.assertEqual(response3b.status_code, 404)
        response3c = self.client.get('/album/api/album3/')
        self.assertEqual(response3c.status_code, 404)

        os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3/first/second'))
        os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3/first'))
        os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3'))

    def tearDown(self):
        try:
            os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3/first/second'))
        except:
            pass
        try:
            os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3/first'))
        except:
            pass
        try:
            os.rmdir(os.path.join(settings.PHOTOS_ROOT_DIR, 'album3'))
        except:
            pass
