from django.test import TestCase
from django.conf import settings
import json
import os
from retrato.album.models import Album
from shutil import rmtree
from django.contrib.auth.models import User


class TestAlbumAdminAcceptance(TestCase):

    def setUp(self):
        self.client.login(username='admin-test', password='1234')

    def tearDown(self):
        self.client.logout()
        for folder in ['album1', 'album2', 'album3/first/second']:
            try:
                os.unlink(os.path.join(settings.BASE_CACHE_DIR, 'album', folder, '.retrato'))
            except:
                pass
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

    @classmethod
    def setUpClass(cls):
        settings.INSTALLED_APPS += ('retrato.admin',)
        cls.admin_user = User.objects.create_superuser('admin-test', 'admin@example.com', '1234')

    @classmethod
    def tearDownClass(cls):
        settings.INSTALLED_APPS = tuple(x for x in settings.INSTALLED_APPS if x != 'retrato.admin')

        cls.admin_user.delete()

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
        photo_link = os.path.join(album_folder, items[1])  # 0 is the .retrato config file
        self.assertTrue(os.path.islink(photo_link))

    def test_make_album_public_should_return_data_on_api_call(self):
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

    def test_make_album_public_should_create_token(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album1")

        if os.path.isdir(album_folder):
            os.rmdir(album_folder)

        response = self.client.post('/admin/album/api/album1/', {'visibility': 'public'})
        self.assertEqual(response.status_code, 200)

        config_file = os.path.join(virtual_folder, "album1", Album.CONFIG_FILE)
        self.assertTrue(os.path.isfile(config_file))
        with open(config_file, 'r') as f:
            content_file = f.read()
        config = json.loads(content_file)

        content = json.loads(response.content)
        self.assertEquals(content['token'], config['token'])

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
