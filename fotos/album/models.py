from django.conf import settings
import os
from os import listdir
from os.path import isfile, join, isdir
import re
import time
from fotos.photo.models import Photo


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
                pictures_name.append(f)
        pictures = [Photo(self._path, f) for f in pictures_name]
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
