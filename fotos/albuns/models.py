from django.conf import settings
import os
from os import listdir
from os.path import isfile, join, isdir
import re
from PIL import Image
from PIL.ExifTags import TAGS
import time


class Album(object):

    _path = '/'
    _realpath = None

    def __init__(self, path="/"):
        self._path = Album.sanitize_path(path)
        self._load()

    def _load(self):
        PHOTOS_ROOT_DIR = getattr(settings, 'PHOTOS_ROOT_DIR', '/')
        self._realpath = os.path.join(PHOTOS_ROOT_DIR, self._path)

    def get_pictures(self):
        if not isdir(self._realpath):
            return []

        extension_re = re.compile('\.jpg$', re.IGNORECASE)
        pictures_name = []
        for f in listdir(self._realpath):
            if f[0] == '.':
                continue
            realfile = os.path.join(self._realpath, f)
            if isfile(realfile) and \
                extension_re.search(f):
                pictures_name.append(realfile)
        pictures = [Picture(f) for f in pictures_name]
        pictures = self._sort_by_date(pictures)
        return pictures

    def _sort_by_date(self, pictures):
        pictures = sorted(pictures, key=lambda p: time.mktime(p.date_taken))
        return pictures

    def get_albuns(self):
        if not isdir(self._realpath):
            return []
        albuns = []
        for f in listdir(self._realpath):
            if f[0] == '.':
                continue
            if isdir(join(self._realpath, f)):
                albuns.append(f)
        return albuns

    @classmethod
    def sanitize_path(clazz, path):
        if not path:
            return ''
        if path[0] == '/':
            path = path[1:]
        path = re.sub('\.+\./', '', path, flags=re.IGNORECASE)
        path = re.sub('/+/', '/', path, flags=re.IGNORECASE)
        return path


class Picture(object):

    _path = None

    name = None
    filename = None
    width = 0
    height = 0
    date_taken = None

    def __init__(self, path):
        self._path = path
        self._load_image_data()

    def _load_image_data(self):
        try:
            img = Image.open(self._path)
            exif = img._getexif()
        except:
            return
        self._load_image_size(img)
        self._load_date_taken(exif)
        self._load_name()

    def _load_date_taken(self, exif):
        str_date = exif.get(306, None)
        if str_date:
            date = time.strptime(str_date, "%Y:%m:%d %H:%M:%S")
        else:
            date = os.path.getmtime(self._path)
        self.date_taken = date

    def _load_name(self):
        fileparts = self._path.split(os.sep)
        filename = fileparts[-1]
        self.filename = filename
        name = re.sub('.jpg', '', filename, flags=re.IGNORECASE)
        name = re.sub('_', ' ', name, flags=re.IGNORECASE)
        self.name = name

    def _load_image_size(self, img):
        size = img.size
        self.width = size[0]
        self.height = size[1]

    def __str__(self):
        return self.name
