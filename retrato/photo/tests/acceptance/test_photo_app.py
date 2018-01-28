from django.test import TestCase
from PIL import Image
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from time import mktime


class TestPhotoAppAcceptance(TestCase):

    DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

    def test_get_image__ok(self):
        response = self.client.get('/photo/album2/photo_1_portrait.JPG')
        self.assertEqual(response.status_code, 200)

    def test_get_image__fail(self):
        response = self.client.get('/photo/album1/picture_does_not_exist.JPG')
        self.assertEqual(response.status_code, 404)

    def test_get_landscape_image(self):
        response = self.client.get('/photo/album2/photo_2.JPG')
        self.assertEqual(response.status_code, 200)
        image = Image.open(BytesIO(response.content))
        size = image.size
        self.assertTrue(size[0] > size[1])

    def test_get_original_image_portrait_rotated(self):
        response = self.client.get('/photo/album2/photo_1_portrait.JPG')
        self.assertEqual(response.status_code, 200)
        image = Image.open(BytesIO(response.content))
        size = image.size
        self.assertTrue(size[0] < size[1])

    def test_image_must_have_size(self):
        response = self.client.get('/photo/album2/photo_2.JPG')
        self.assertEqual(response.status_code, 200)
        content_length = int(response.get('Content-Length'))
        self.assertTrue(content_length > 0)

    def test_image_must_have_time(self):
        response = self.client.get('/photo/album2/photo_2.JPG')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get('Last-Modified'))

    def test_image_resize(self):
        response = self.client.get('/photo/album2/photo_2.JPG?size=1000')
        self.assertEqual(response.status_code, 200)
        image = Image.open(BytesIO(response.content))
        size = image.size
        self.assertEquals(size[0], 1000)

    def test_image_not_modified(self):
        time_cache = datetime.now() + timedelta(0, 60)
        time_cachestr_time = time_cache.strftime(self.DATE_FORMAT)
        response = self.client.get('/photo/album2/photo_2.JPG?size=1000', \
                                   **{'HTTP_IF_MODIFIED_SINCE': time_cachestr_time})
        self.assertEqual(response.status_code, 304)

    def test_image_modified(self):
        time_cache = datetime(2013, 1, 1)
        time_cachestr_time = time_cache.strftime(self.DATE_FORMAT)
        response = self.client.get('/photo/album2/photo_2.JPG?size=1000', \
                                   **{'HTTP_IF_MODIFIED_SINCE': time_cachestr_time})
        self.assertEqual(response.status_code, 200)