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

    name = None
    width = 0
    height = 0
    date_taken = None
    url = None

    def __init__(self, album, filename):
        self.album = album
        self.filename = filename
        self._load_image_data()

    def _real_file(self):
        PHOTOS_ROOT_DIR = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        folder = os.path.join(PHOTOS_ROOT_DIR, self.album)
        self.real_filename = os.path.join(folder, self.filename)

    def _load_image_data(self):
        self._real_file()
        try:
            img = Image.open(self.real_filename)
            exif = img._getexif()
        except:
            return
        self._load_image_size(img)
        self._load_date_taken(exif)
        self._load_name()
        self._loaf_url()

    def _load_date_taken(self, exif):
        str_date = exif.get(306, None)
        if str_date:
            date = time.strptime(str_date, "%Y:%m:%d %H:%M:%S")
        else:
            date = os.path.getmtime(self._path)
        self.date_taken = date

    def _load_name(self):
        name = re.sub('.jpg', '', self.filename, flags=re.IGNORECASE)
        name = re.sub('_', ' ', name)
        self.name = name

    def _load_image_size(self, img):
        size = img.size
        self.width = size[0]
        self.height = size[1]

    def _loaf_url(self):
        photo = '%s/%s' % (self.album, self.filename)
        photo = re.sub('/+', '/', photo)
        url = reverse('photo', args=(photo,))
        self.url = url

    def exists(self):
        return os.path.isfile(self.real_filename)

    def __str__(self):
        return self.name
