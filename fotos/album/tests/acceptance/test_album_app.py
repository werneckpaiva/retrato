from django.test import TestCase
import json


class TestAlbumAppAcceptance(TestCase):

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)

    def test_load_default_album(self):
        response = self.client.get('/album/api/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/')
        self.assertTrue(len(content['albuns']) >= 2)
        self.assertEquals(content['pictures'], [])

    def test_load_test_album__no_pictures(self):
        response = self.client.get('/album/api/album1/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/album1/')
        self.assertEquals(len(content['albuns']), 0)
        self.assertEquals(len(content['pictures']), 0)

    def test_load_test_album__4_pictures(self):
        response = self.client.get('/album/api/album2/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/album2/')
        self.assertEquals(len(content['albuns']), 0)
        self.assertEquals(len(content['pictures']), 4)

        pictures = content['pictures']
        self.assertEquals(pictures[0]["name"], 'photo first')
        self.assertEquals(pictures[0]["filename"], 'photo_first.JPG')
        self.assertEquals(pictures[0]["width"], 3008)
        self.assertEquals(pictures[0]["height"], 2000)
        self.assertEquals(pictures[0]["date"], '2013-03-01 14:48:25')
        self.assertEquals(pictures[0]["ratio"], 1.504)
        self.assertEquals(pictures[0]["url"], '/photo/album2/photo_first.JPG')
        self.assertEquals(pictures[0]["thumb"], '/photo/album2/photo_first.JPG?size=640')
