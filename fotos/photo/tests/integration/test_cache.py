from django.test import TestCase
from django.conf import settings
from fotos.photo.models import Photo
from fotos.photo.models import PhotoCache
import os
from PIL import Image


class TestPhotoCacheIntegration(TestCase):

    def _remove_cache(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

    def test_create_cache_and_check_if_exists(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')
        cache = PhotoCache(photo)

        self._remove_cache(cache.get_filename())

        self.assertFalse(cache.is_in_cache())
        cache.create_cache()
        self.assertTrue(cache.is_in_cache())

    def test_create_and_load_from_cache(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')
        cache = PhotoCache(photo)

        self._remove_cache(cache.get_filename())

        self.assertFalse(cache.is_in_cache())
        cache_file = cache.get_file()
        assert cache_file
        self.assertTrue(cache.is_in_cache())

        BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
        photos_cache_dir = os.path.join(BASE_CACHE_DIR, "photo")
        self.assertTrue(cache_file.startswith(photos_cache_dir))
        self.assertNotEquals(photo.real_filename, cache_file)

    def test_load_from_cache(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')
        cache = PhotoCache(photo)

        self._remove_cache(cache.get_filename())
        self.assertFalse(cache.is_in_cache())
        cache.create_cache()
        self.assertTrue(cache.is_in_cache())

        cache_file = cache.get_file()
        assert cache_file

        BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
        photos_cache_dir = os.path.join(BASE_CACHE_DIR, "photo")
        self.assertTrue(cache_file.startswith(photos_cache_dir))

    def test_load_resized_image(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_first.JPG')
        img = Image.open(photo.real_filename)
        self.assertEquals(img.size[0], 3008)

        cache = PhotoCache(photo)

        self._remove_cache(cache.get_filename())
        self.assertFalse(cache.is_in_cache())

        cache.set_max_dimension(800)
        cache_file = cache.get_file()

        img = Image.open(cache_file)
        size = img.size
        self.assertEquals(size[0], 800)

    def test_load_rotated_image(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        photo = Photo(root_folder, "album2", 'photo_1_portrait.JPG')
        img = Image.open(photo.real_filename)
        self.assertTrue(img.size[0] > img.size[1])

        cache = PhotoCache(photo)

        self._remove_cache(cache.get_filename())
        self.assertFalse(cache.is_in_cache())

        cache.rotate_based_on_orientation()
        cache_file = cache.get_file()

        img = Image.open(cache_file)
        self.assertTrue(img.size[0] < img.size[1])

    def test_cache_folder(self):
        root_folder = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        album_name = "album2"
        photo_name = 'photo_1_portrait.JPG'
        photo = Photo(root_folder, album_name, photo_name)
        cache = PhotoCache(photo)
        cache_file = cache.get_file()

        self.assertTrue(cache_file.find(album_name) >= 0)
