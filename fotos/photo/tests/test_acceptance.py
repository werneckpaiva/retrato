from django.test import TestCase


class TestPhotoAcceptance(TestCase):

    def test_get_image__ok(self):
        response = self.client.get('/photo/album2/photo_1.JPG')
        self.assertEqual(response.status_code, 200)

    def test_get_image__fail(self):
        response = self.client.get('/photo/album1/picture_does_not_exist.JPG')
        self.assertEqual(response.status_code, 404)
