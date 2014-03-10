from django.conf import settings
from django.core.urlresolvers import reverse
import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import time
from django.http import HttpResponse


class Photo(object):

    album = None
    filename = None
    real_filename = None
    image = None
    exif = None

    name = None
    width = 0
    height = 0
    date_taken = None
    url = None

    def __init__(self, album, filename):
        self.album = album
        self.filename = filename
        self._real_file()

    def _real_file(self):
        PHOTOS_ROOT_DIR = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        folder = os.path.join(PHOTOS_ROOT_DIR, self.album)
        self.real_filename = os.path.join(folder, self.filename)

    def open_image(self):
        # is image already opened?
        if self.image:
            return
        self.image = Image.open(self.real_filename)

    def close_image(self):
        if not self.image:
            return
        del self.image
        self.image = None

    def load_exif(self):
        if (self.exif):
            return
        self.open_image()
        self.exif = self.image._getexif()

    def load_image_data(self):
        self.open_image()
        self.load_exif()

        self.load_image_size()
        self.load_date_taken()
        self.load_name()
        self.load_url()

    def load_date_taken(self):
        self.load_exif()
        str_date = self.exif.get(306, None)
        if str_date:
            date = time.strptime(str_date, "%Y:%m:%d %H:%M:%S")
        else:
            date = os.path.getmtime(self._path)
        self.date_taken = date

    def load_name(self):
        name = re.sub('.jpg', '', self.filename, flags=re.IGNORECASE)
        name = re.sub('_', ' ', name)
        self.name = name

    def load_image_size(self):
        self.open_image()
        size = self.image.size
        rotation = self.get_orientation_angle()
        if rotation == 0 or rotation == 180:
            self.width = size[0]
            self.height = size[1]
        else:
            self.width = size[1]
            self.height = size[0]

    def load_url(self):
        photo = '%s/%s' % (self.album, self.filename)
        photo = re.sub('/+', '/', photo)
        url = reverse('photo', args=(photo,))
        self.url = url

    def exists(self):
        return os.path.isfile(self.real_filename)

    def get_image(self):
        self.open_image()
        return self.image

    def rotate_based_on_orientation(self):
        self.open_image()
        rotation = self.get_orientation_angle()
        if not rotation:
            return False
        self.image = self.image.rotate(rotation)
        return True

    def resize_max_dimension(self, dimension):
        self.open_image()
        size = self.image.size
        ratio = float(size[0]) / float(size[1])
        if ratio > 0:
            newWidth = dimension
            self.image = self.image.resize((newWidth, int(newWidth / ratio)), Image.ANTIALIAS)
        else:
            newHeight = dimension
            self.image = self.image.resize((newHeight, int(newHeight / ratio)), Image.ANTIALIAS)

    def get_orientation_angle(self):
        self.load_exif()
        angles = {1: 0, 8: 90, 3: 180, 3: 270}
        orientation = self.exif.get(274, None)
        angle = angles.get(orientation, 0)
        return angle

    def __str__(self):
        return self.name
