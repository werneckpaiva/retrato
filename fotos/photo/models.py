from django.conf import settings
from django.core.urlresolvers import reverse
import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import time


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
        # is image alreasy opened?
        if self.image:
            return
        try:
            self.image = Image.open(self.real_filename)
        except:
            return

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
        self.loaf_url()

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

    def loaf_url(self):
        photo = '%s/%s' % (self.album, self.filename)
        photo = re.sub('/+', '/', photo)
        url = reverse('photo', args=(photo,))
        self.url = url

    def exists(self):
        return os.path.isfile(self.real_filename)

    def save_to_response(self, response):
        self.open_image()
        rotation = self.get_orientation_angle()
        img = self.image
        if rotation:
            img = self.image.rotate(rotation)
        img.save(response, "JPEG")
        return response

    def get_orientation_angle(self):
        self.load_exif()
        angles = {1: 0, 8: 90, 3: 180, 3: 270}
        orientation = self.exif.get(274, None)
        angle = angles.get(orientation, 0)
        return angle

    def __str__(self):
        return self.name
