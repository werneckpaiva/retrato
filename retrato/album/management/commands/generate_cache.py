import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from retrato.album.models import Album
from retrato.photo.models.photo_cache import PhotoCache


class Command(BaseCommand):

    help = 'Generate image caches for all albuns'

    def handle(self, *args, **options):
        path = '/'
        if len(args) > 0:
            path = args[0]
        root_album = Album(settings.PHOTOS_ROOT_DIR, path)
        self.create_cache_for_album(root_album)

    def create_cache_for_album(self, album):
        print "Album: %s" % album.path
        for picture in album.get_pictures():
            self.create_cache(picture)

        for sub_album_path in album.get_albuns():
            path = os.path.join(album.path, sub_album_path)
            sub_album = Album(settings.PHOTOS_ROOT_DIR, path)
            self.create_cache_for_album(sub_album)

    def create_cache(self, picture):
        cache = PhotoCache(picture)
        cache.rotate_based_on_orientation()
        cache.set_max_dimension(640)
        if not cache.is_in_cache():
            print "Creating cache %s" % cache.filename
            cache.create_cache()
