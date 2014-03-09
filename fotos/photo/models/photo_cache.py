from django.conf import settings
import os
import re
import logging
import hashlib

logger = logging.getLogger(__name__)


class PhotoCache(object):
    photo = None

    filename = None

    _operations = {}

    should_rotate = False
    should_resize_to = None

    def __init__(self, photo):
        self.photo = photo

    def checksum(self, filename, blocksize=65536):
        checksum = hashlib.md5()
        with open(filename, "r+b") as f:
            for block in iter(lambda: f.read(blocksize), ""):
                checksum.update(block)
        return checksum.hexdigest()

    def generate_filename(self):
        PHOTOS_CACHE_DIR = getattr(settings, 'PHOTOS_CACHE_DIR', '/')
        photo_dir = "%s/%s/" % (PHOTOS_CACHE_DIR, self.photo.album)
        if not os.path.exists(photo_dir):
            os.makedirs(photo_dir)
        filename = self.checksum(self.photo.real_filename)
        for (op, value) in self._operations.items():
            if isinstance(value, bool):
                filename += ".%s" % op
            else:
                filename += ".%s_%s" % (op, value)
        filename = "%s.%s" % (filename, self.photo.filename)
        filename = "%s/%s" % (photo_dir, filename)
        filename = re.sub('/+/', '/', filename)
        filename = re.sub('\.+\./', '', filename)
        self.filename = filename

    def get_filename(self):
        if not self.filename:
            self.generate_filename()
        return self.filename

    def create_cache(self):
        if self.should_resize_to:
            self.photo.rotate_based_on_orientation()
        if self.should_resize_to:
            self.photo.resize_max_dimension(self.should_resize_to)
        self.generate_filename()
        photo = self.photo.get_image()
        photo.save(self.filename, "JPEG")

    def is_in_cache(self):
        filename = self.get_filename()
        return os.path.isfile(filename)

    def get_file(self):
        if not self.is_in_cache():
            logger.info("Cache miss (%s)" % self.get_filename())
            self.create_cache()
        else:
            logger.info("Cache hit (%s)" % self.get_filename())
        return self.filename

    def set_max_dimension(self, size):
        self.should_resize_to = size
        self._operations['size'] = size

    def rotate_based_on_orientation(self):
        self.should_rotate = True
