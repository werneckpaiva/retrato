from django.test import TestCase


class TestAlbumAdminAcceptance(TestCase):

    def test_load_admin_page(self):
        response = self.client.get('/admin/album/')
        self.assertEqual(response.status_code, 200)
