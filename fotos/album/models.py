import os
from os import listdir
from os.path import isfile, join, isdir
import re
import time
from fotos.photo.models import Photo


class Album(object):

    _path = '/'
    _realpath = None
    _root_folder = None

    def __init__(self, root_folder, path="/"):
        self._path = Album.sanitize_path(path)
        self._root_folder = root_folder
        self._load()

    def _load(self):
        self._realpath = os.path.join(self._root_folder, self._path)

    @property
    def root_folder(self):
        return self._root_folder

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
        pictures = [Photo(self._root_folder, self._path, f) for f in pictures_name]
        for p in pictures:
            p.load_date_taken()
            p.close_image()
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
        albuns = sorted(albuns)
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
