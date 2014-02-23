from django.test import TestCase
import json


class TestAlbum(TestCase):

    def test_load_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'albuns/index.html')

    def test_load_default_album(self):
        response = self.client.get('/album/')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/')

    def test_load_test_album(self):
        response = self.client.get('/album/trips/europe')

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assert_(content)
        self.assertEquals(content['album'], '/trips/europe')
