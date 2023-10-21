import re
from typing import Dict, Any


class GdrivePhoto:
    album = None

    name = None
    filename = None
    width = None
    height = None
    ratio = None
    date_taken = None

    url = None
    thumb = None
    highlight = None

    def __init__(self, album, photo: Dict[str, Any]):
        self.album = album
        self.id = photo["id"]
        self.filename = photo["name"]
        self.name = self.sanitize_name(self.filename)
        media_data = photo["imageMediaMetadata"]

        rotation = media_data.get("rotation", 0)
        if rotation == 0 or rotation == 2:
            self.width = media_data["width"]
            self.height = media_data["height"]
        else:
            self.width = media_data["height"]
            self.height = media_data["width"]

        self.ratio = float(self.width) / float(self.height)
        self.date_taken = media_data.get("time", None)

        self.url = photo["webContentLink"]
        self.thumb = self.build_thumb(photo["thumbnailLink"])
        self.highlight = self.build_highlight(photo["thumbnailLink"])

    @property
    def path(self):
        return self._path

    def sanitize_name(self, filename):
        name = re.sub('.jpg', '', self.filename, flags=re.IGNORECASE)
        name = re.sub('_', ' ', name)
        return name

    def build_thumb(self, url):
        new_url = re.sub(r'=s\d+$', r'=s640', url)
        return new_url

    def build_highlight(self, url):
        new_url = re.sub(r'=s\d+$', r'=s1440', url)
        return new_url

    def __str__(self):
        return self.name

    def relative_url(self):
        relative_url = f'{self.album.path}/{self.filename}'
        return relative_url
