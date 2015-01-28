import json
import re
import time
import uuid
import hashlib
import logging
import os
from os import listdir
from os.path import isfile, join, isdir
from django.conf import settings
from retrato.photo.models import Photo


logger = logging.getLogger(__name__)


class AlbumError(Exception):
    pass


class AlbumNotFoundError(AlbumError):
    pass


class Album(object):

    VISIBILITY_PUBLIC = "public"
    VISIBILITY_PRIVATE = "private"

    CONFIG_FILE = ".retrato"

    _path = '/'
    _realpath = None
    _root_folder = None

    def __init__(self, root_folder, path="/"):
        self._path = Album.sanitize_path(path)
        self._root_folder = root_folder
        self._load()

    def _load(self):
        self._realpath = os.path.join(self._root_folder, self._path)
        if not os.path.isdir(self._realpath):
            raise AlbumNotFoundError()

    @property
    def path(self):
        return self._path

    @property
    def root_folder(self):
        return self._root_folder

    def get_all_pictures_name(self):
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
        return pictures_name

    def get_pictures(self):
        pictures_name = self.get_all_pictures_name()
        pictures = [Photo(self._root_folder, self._path, f) for f in pictures_name]
#         pictures = self._sort_by_date(pictures)
        pictures = self._sort_by_date(pictures)
        return pictures

    def _sort_by_date(self, pictures):
        def date_taken_key(p):
            p.load_date_taken()
            p.close_image()
            return time.mktime(p.date_taken)
        pictures = sorted(pictures, key=date_taken_key)
        return pictures

    def _sort_by_name(self, pictures):
        pictures = sorted(pictures, key=str.lower)
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

    def get_visibility(self):
        virtual_folder = self.get_virtual_album()
        if os.path.isdir(virtual_folder):
            return Album.VISIBILITY_PUBLIC
        else:
            return Album.VISIBILITY_PRIVATE

    def set_visibility(self, visibility):
        if visibility == Album.VISIBILITY_PUBLIC:
            self.make_all_photos_public()
        elif visibility == Album.VISIBILITY_PRIVATE:
            self.make_it_private()
        else:
            raise Exception('Undefined visibility')

    def make_all_photos_public(self):
        self.make_it_public()
        pictures_name = self.get_all_pictures_name()
        virtual_folder = self.get_virtual_album()
        for picture in pictures_name:
            photo_file = os.path.join(self._realpath, picture)
            virtual_file = os.path.join(virtual_folder, picture)
            if not os.path.islink(virtual_file):
                os.symlink(photo_file, virtual_file)

    @classmethod
    def get_virtual_base_folder(cls):
        BASE_CACHE_DIR = getattr(settings, 'BASE_CACHE_DIR', '/')
        album_virtual_folder = os.path.join(BASE_CACHE_DIR, "album")
        return album_virtual_folder

    def get_virtual_album(self):
        album_virtual_folder = Album.get_virtual_base_folder()
        virtual_folder = os.path.join(album_virtual_folder, self._path)
        return virtual_folder

    def make_it_public(self):
        virtual_folder = self.get_virtual_album()
        if not os.path.isdir(virtual_folder):
            os.makedirs(virtual_folder)
        self.create_config()

    def make_it_private(self):
        virtual_folder = self.get_virtual_album()
        for picture in os.listdir(virtual_folder):
            virtual_file = os.path.join(virtual_folder, picture)
            if not os.path.islink(virtual_file) and picture != self.CONFIG_FILE:
                raise Exception('Can\'t make the album private')
            os.unlink(virtual_file)
        path = virtual_folder.rstrip('/')
        base_folder = Album.get_virtual_base_folder()
        while path != '/' and len(path) > len(base_folder):
            if os.listdir(path) == []:
                os.rmdir(path)
            else:
                break
            (path, current_folder) = os.path.split(path)

    def get_photo_visibility(self, picture):
        virtual_folder = self.get_virtual_album()
        virtual_file = os.path.join(virtual_folder, picture)
        if os.path.islink(virtual_file):
            return Album.VISIBILITY_PUBLIC
        else:
            return Album.VISIBILITY_PRIVATE

    def set_photo_visibility(self, photo_filename, visibility):
        virtual_folder = self.get_virtual_album()
        virtual_file = os.path.join(virtual_folder, photo_filename)
        link_exists = os.path.islink(virtual_file)

        if visibility == Album.VISIBILITY_PUBLIC and not link_exists:
            self.make_it_public()
            photo_file = os.path.join(self._realpath, photo_filename)
            os.symlink(photo_file, virtual_file)
        elif visibility == Album.VISIBILITY_PRIVATE and link_exists:
            os.unlink(virtual_file)

    def config(self):
        virtual_folder = self.get_virtual_album()
        config_filename = join(virtual_folder, self.CONFIG_FILE)
        if (not os.path.isfile(config_filename)
            or not os.access(config_filename, os.R_OK)):
            return {}
        with open(config_filename, 'r') as f:
            content = f.read()
        config = json.loads(content)
        return config

    def create_config(self):
        config = self.config()
        if config is None:
            config = {}
        if 'token' not in config:
            config['token'] = self._generate_token()
        self._save_config(config)

    def _save_config(self, config):
        virtual_folder = self.get_virtual_album()
        config_filename = join(virtual_folder, self.CONFIG_FILE)
        with open(config_filename, 'w') as f:
            json.dump(config, f, indent=4)

    def _generate_token(self):
        return hashlib.sha224(str(uuid.uuid4())).hexdigest()

    def get_token(self):
        config = self.config()
        return config['token'] if config is not None and 'token' in config else None

    def get_cover(self):
        config = self.config()
        # get from config
        if 'cover' in config:
            return Photo(self._root_folder, self._path, config['cover'])
        # get default
        picture_names = self.get_all_pictures_name()
        if picture_names is None or len(picture_names) == 0:
            return None
        cover = Photo(self._root_folder, self._path, picture_names[0])
        return cover

    def set_cover(self, photo_filename):
        picture_names = self.get_all_pictures_name()
        if photo_filename not in picture_names:
            raise AlbumError("File '%s' does not exist in album %s" % (photo_filename, self._path))
        config = self.config()
        config['cover'] = photo_filename
        self._save_config(config)

    def get_parent(self):
        path = Album.sanitize_path(self.path)
        parts = path.split('/')
        parts = parts[:-1]
        parent_path = '/'.join(parts)
        if parent_path == '' or parent_path == '/':
            return None
        return Album(self.root_folder, parent_path)
