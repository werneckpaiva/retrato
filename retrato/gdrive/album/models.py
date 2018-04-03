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
    _content = None

    _config = None
    _config_file_id = None
    _albuns = []
    _pictures = []

    def __init__(self, gdrive_service, album_id):
        self._gdrive = gdrive_service
        self._album_id = album_id

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
                fields="nextPageToken, files(id, name, mimeType, createdTime, imageMediaMetadata, thumbnailLink, webContentLink)",
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
        self._albuns = sorted(folders, key=lambda x: x["name"])

    def get_albuns(self):
        return [album["name"] for album in self._albuns]

    def get_pictures(self):
        pictures = [GdrivePhoto(p) for p in self._pictures]
        pictures = self.sort_by_name(pictures)
        return pictures

    def sort_by_name(self, pictures):
        pictures = sorted(pictures, key=lambda p: str(p).lower())
        return pictures

    def get_config(self):
        if self._config_file_id is None:
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
        self._config = json.loads(fh.getvalue())

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
        config = self.get_config()
        if config:
            return config["visibility"]
        else:
            return BaseAlbum.VISIBILITY_PRIVATE

    def make_it_public(self):
        config = self.get_config()
        config["visibility"] = BaseAlbum.VISIBILITY_PUBLIC

        self.load_content()
        config["pictures"] = []
        for picture in self._pictures:
            config["pictures"].append({
                "name": picture["name"],
                "id": picture["id"]
            })

        self.save_config(config)

    def make_it_private(self):
        config = self.get_config()
        config["visibility"] = BaseAlbum.VISIBILITY_PRIVATE
        config["pictures"] = []
        self.save_config(config)

    def get_token(self):
        return "1234"

    def get_photo_visibility(self, picture):
        return BaseAlbum.VISIBILITY_PUBLIC

