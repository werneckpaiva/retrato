from django.test import TestCase
from django.conf import settings
import json
import os
from retrato.album.models import Album, BaseAlbum
from django.contrib.auth.models import User


class TestAlbumPictureAdminAcceptance(TestCase):

    def setUp(self):
        self.client.login(username='admin-test', password='1234')

    def tearDown(self):
        self.client.logout()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.INSTALLED_APPS += ('retrato.admin',)
        cls.admin_user = User.objects.create_superuser('admin-test', 'admin@example.com', '1234')

    @classmethod
    def tearDownClass(cls):
        settings.INSTALLED_APPS = tuple(x for x in settings.INSTALLED_APPS if x != 'retrato.admin')
        cls.admin_user.delete()
        super().tearDownClass()

    def test_public_album_all_pictures_are_public(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        response1 = self.client.post('/admin/album/api/album2/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response = self.client.get('/admin/album/api/album2/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        for picture in content['pictures']:
            self.assertEquals(picture['visibility'], BaseAlbum.VISIBILITY_PUBLIC)

    def test_make_picture_private(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        response1 = self.client.post('/admin/album/api/album2/', {'visibility': 'public'})
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(os.path.isdir(album_folder))

        response2 = self.client.get('/admin/album/api/album2/')
        self.assertEqual(response2.status_code, 200)
        content = json.loads(response2.content)
        self.assertEquals(content['pictures'][0]['visibility'], BaseAlbum.VISIBILITY_PUBLIC)

        url = '/admin/photo/album2/%s' % content['pictures'][0]['filename']
        response3 = self.client.post(url, {'visibility': 'private'})
        self.assertEqual(response3.status_code, 200)
        content = json.loads(response3.content)
        self.assertEquals(content['visibility'], BaseAlbum.VISIBILITY_PRIVATE)

    def test_make_picture_public(self):
        virtual_folder = Album.get_virtual_base_folder()
        album_folder = os.path.join(virtual_folder, "album2")

        response1 = self.client.post('/admin/album/api/album2/', {'visibility': 'private'})
        self.assertEqual(response1.status_code, 200)
        self.assertFalse(os.path.isdir(album_folder))

        response = self.client.get('/album/api/album2/')
        self.assertEqual(response.status_code, 404)

        url = '/admin/photo/album2/photo_2.JPG'
        response3 = self.client.post(url, {'visibility': 'public'})
        self.assertEqual(response3.status_code, 200)
        content = json.loads(response3.content)
        self.assertEquals(content['visibility'], BaseAlbum.VISIBILITY_PUBLIC)

        response2 = self.client.get('/admin/album/api/album2/')
        self.assertEqual(response2.status_code, 200)
        content = json.loads(response2.content)
        photo = None
        for f in content['pictures']:
            if f['filename'] == 'photo_2.JPG':
                photo = f
        self.assertEquals(photo['visibility'], BaseAlbum.VISIBILITY_PUBLIC)
