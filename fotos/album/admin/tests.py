from django.test import TestCase
import json


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

    def 