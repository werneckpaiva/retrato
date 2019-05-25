import io
import json

from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from io import StringIO, BytesIO

from retrato.album.models import Album, AlbumNotFoundError, BaseAlbum
from retrato.gdrive.photo.models import GdrivePhoto


class GdriveAlbum(BaseAlbum):

    MIME_FOLDER = 'application/vnd.google-apps.folder'
    CONFIG_FILE = ".retrato"

    _gdrive = None
    _album_id = None

    _folder_details = None
    _parent_folder_id = None

    _config = None
    _config_file_id = None
    _albums = []
    _pictures = []

    def __init__(self, gdrive_service, album_id):
        self._gdrive = gdrive_service
        self._album_id = album_id

    def load_folder_details(self):
        self._folder_details = self._gdrive.files().get(
            fileId=self._album_id,
            fields="id, name, parents"
        ).execute()
        self._parent_folder_id = self._folder_details.get("parents", [None])[0]

    def load_content(self):
        ITEMS_PER_CALL = 100
        folders = []
        files = []
        param = {}
        while True:
            results = self._gdrive.files().list(
                corpora="user",
                q="parents='%s' and (mimeType='image/jpeg' or mimeType='application/vnd.google-apps.folder')" % self._album_id,
                pageSize=ITEMS_PER_CALL,
                spaces='drive',
                fields="nextPageToken, files(id, name, mimeType, createdTime, imageMediaMetadata, thumbnailLink, webContentLink, appProperties)",
                **param).execute()

            items = results.get('files', [])
            for item in items:
                if item["name"].startswith("."):
                    continue
                if item['mimeType'] == GdriveAlbum.MIME_FOLDER:
                    folders.append(item)
                else:
                    files.append(item)
            if not items or len(items) < ITEMS_PER_CALL:
                break

            param['pageToken'] = results.get("nextPageToken")
            if (not param['pageToken']):
                break
        self._pictures = sorted(files, key=lambda x: x["name"])
        self._albums = sorted(folders, key=lambda x: x["name"])

    def get_albums(self):
        return [album["name"] for album in self._albums]

    def get_public_albums(self):
        public_albums = [album["name"] for album in self._albums if
                   album.get("appProperties", {}).get("visibility", {}) == BaseAlbum.VISIBILITY_PUBLIC]
        return public_albums

    def get_pictures(self):
        pictures = [GdrivePhoto(p) for p in self._pictures]
        pictures = self.sort_by_name(pictures)
        return pictures

    def sort_by_name(self, pictures):
        pictures = sorted(pictures, key=lambda p: str(p).lower())
        return pictures

    def config(self):
        if self._config_file_id is None or self._config is None:
            self.load_config()
        return self._config

    def load_config(self):
        results = self._gdrive.files().list(
            corpora="user",
            q="parents='%s' and name='%s'" % (self._album_id, GdriveAlbum.CONFIG_FILE),
            pageSize=1,
            spaces='drive').execute()
        items = results.get('files', [])
        if len(items) == 0:
            self._config_file_id = ''
            self._config = {} # TODO new config with default values
            return
        config_item = items[0]
        self._config_file_id=config_item["id"]
        request = self._gdrive.files().get_media(fileId=self._config_file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        while True:
            _, done = downloader.next_chunk()
            if done: break
        config = json.loads(fh.getvalue())
        if "albuns" not in config:
            config["albuns"] = []
        if "pictures" not in config:
            config["pictures"] = []
        self._config = config

    def save_config(self, config):
        fh = BytesIO(str.encode(json.dumps(config)))
        media = MediaIoBaseUpload(fh, mimetype='plain/text', chunksize=1024 * 1024, resumable=True)
        if self._config_file_id:
            self._gdrive.files().update(body={},
                                         media_body=media,
                                         fields='id',
                                         fileId=self._config_file_id).execute()
        else:
            file_metadata = {
                'name': GdriveAlbum.CONFIG_FILE,
                'parents': [self._album_id]
            }
            result = self._gdrive.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
            self._config_file_id = result.get('id')
        self._config = config

    def get_visibility(self):
        config = self.config() or {}
        return config.get("visibility", BaseAlbum.VISIBILITY_PRIVATE)


    def make_it_public(self):

        config = self.config()
        config["visibility"] = BaseAlbum.VISIBILITY_PUBLIC
        self.save_config(config)

        self.change_visibility_recursively(BaseAlbum.VISIBILITY_PUBLIC)

    def make_it_private(self):

        config = self.config()
        config["pictures"] = []

        # Make it
        if len(config.get("albuns", [])) == 0:


        self.save_config(config)

        self.change_visibility_recursively(BaseAlbum.VISIBILITY_PRIVATE)

    def change_visibility_recursively(self, visibility):
        self.load_folder_details()
        parent_album = GdriveAlbum(self._gdrive, self._parent_folder_id)
        parent_album.set_child_album_visibility(visibility, self._album_id)
        parent_album.set_visibility(visibility)


    def set_gdrive_property(self, properties):
        body = {'appProperties': properties}
        updated_file = self._gdrive.files().update(
            body=body,
            fileId=self._album_id,
            fields='id, appProperties'
        ).execute()
        return updated_file

    def set_child_album_visibility(self, visibility, child_album_id):
        config = self.config()
        albums = set(config.get("albums", []))
        if visibility == BaseAlbum.VISIBILITY_PUBLIC:
            albums.add(child_album_id)
        else:
            if child_album_id in albums:
                albums.remove(child_album_id)
            else:
                return
        config["albums"] = list(albums)
        self.save_config(config)


    def get_photo_visibility(self, picture):
        return BaseAlbum.VISIBILITY_PUBLIC
