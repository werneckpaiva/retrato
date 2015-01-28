import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
import time


class Photo(object):

    base_folder = None
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

    def __init__(self, base_folder, album, filename):
        self.base_folder = base_folder
        self.album = album
        self.filename = filename
        self._real_file()

    def _real_file(self):
        folder = os.path.join(self.base_folder, self.album)
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

    def load_date_taken(self):
        self.load_exif()
        str_date = self.exif.get(306, None) if self.exif else None 
        if str_date:
            date = time.strptime(str_date, "%Y:%m:%d %H:%M:%S")
        else:
            date = time.gmtime(os.path.getmtime(self.real_filename))
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

    def relative_url(self):
        relative_url = '%s/%s' % (self.album, self.filename)
        relative_url = re.sub('/+', '/', relative_url)
        return relative_url

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
        angles = {1: 0, 8: 90, 3: 180, 6: 270}
        orientation = self.exif.get(274, None) if self.exif else None
        angle = angles.get(orientation, 0)
        return angle

    def __str__(self):
        if self.name is None:
            self.load_name()
        return self.name
