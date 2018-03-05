from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings
import os
import json
from retrato.album.models import Album


class TestAlbumAuth(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user1 = User.objects.create_superuser('user1', 'user1@example.com', '1234')
        settings.REQUIRE_AUTHENTICATION = True

    @classmethod
    def tearDownClass(cls):
        cls.user1.delete()
        settings.REQUIRE_AUTHENTICATION = False

    def test_user_not_authenticated_rejected(self):
        client = Client()
        response = client.get('/album/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login?next=/album/'))

    def test_api_user_not_authenticated_rejected(self):
        client = Client()
        response = client.get('/album/api/')
        self.assertEqual(response.status_code, 401)

    def test_user_authenticated_accepted(self):
        client = Client()
        client.login(username='user1', password='1234')
        response = client.get('/album/album1')
        self.assertEqual(response.status_code, 200)
        client.logout()

    def test_api_user_authenticated_accepted(self):
        client = Client()
        client.login(username='user1', password='1234')
        response = client.get('/album/api/album1')
        self.assertEqual(response.status_code, 200)
        client.logout()

    def test_user_with_valid_token(self):
        # save .retrato file
        album_folder = os.path.join(settings.BASE_CACHE_DIR, 'album', 'album2')
        try:
            os.mkdir(album_folder)
        except:
            pass
        retrato_file = os.path.join(album_folder, Album.CONFIG_FILE)
        with open(retrato_file, 'w') as json_file:
            json.dump({'token': 1234}, json_file)

        client = Client()
        response = client.get('/album/album2?token=1234')
        self.assertEqual(response.status_code, 200)

        response = client.get('/album/api/album2?token=1234')
        self.assertEqual(response.status_code, 200)

        os.remove(retrato_file)

    def test_user_with_invalid_token(self):
        # save .retrato file
        album_folder = os.path.join(settings.BASE_CACHE_DIR, 'album', 'album2')
        try:
            os.mkdir(album_folder)
        except:
            pass
        retrato_file = os.path.join(album_folder, Album.CONFIG_FILE)
        with open(retrato_file, 'w') as json_file:
            json.dump({'token': 1234}, json_file)

        client = Client()
        response = client.get('/album/album2?token=5678')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/login?next=/album/album2'))

        os.remove(retrato_file)

    def test_user_with_valid_token_for_subfolder_invalid_for_root_folder(self):
        # TODO
        pass
