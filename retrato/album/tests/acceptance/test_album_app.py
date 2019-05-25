from django.test import TestCase
import json


class TestAlbumAppAcceptanceWithoutAuth(TestCase):

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response.url.endswith('/album/'))

    def test_load_default_album(self):
        response = self.client.get('/album/api/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['path'], '/')
        self.assertTrue(len(content['albums']) >= 2)
        self.assertEquals(content['pictures'], [])

    def test_load_test_album__no_pictures(self):
        response = self.client.get('/album/api/album1/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['path'], '/album1/')
        self.assertEquals(len(content['albums']), 0)
        self.assertEquals(len(content['pictures']), 0)

    def test_load_test_album__4_pictures(self):
        response = self.client.get('/album/api/album2/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['path'], '/album2/')
        self.assertEquals(len(content['albums']), 0)
        self.assertEquals(len(content['pictures']), 4)

        pictures = content['pictures']
        self.assertEquals(pictures[3]["name"], 'photo first')
        self.assertEquals(pictures[3]["filename"], 'photo_first.JPG')
        self.assertEquals(pictures[3]["width"], 3008)
        self.assertEquals(pictures[3]["height"], 2000)
        self.assertEquals(pictures[3]["date"], '2013-03-01 14:48:25')
        self.assertEquals(pictures[3]["ratio"], 1.504)
        self.assertEquals(pictures[3]["url"], '/photo/album2/photo_first.JPG')
        self.assertEquals(pictures[3]["thumb"], '/photo/album2/photo_first.JPG?size=640')
