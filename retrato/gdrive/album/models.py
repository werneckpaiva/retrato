from googleapiclient.errors import HttpError

from retrato.album.models import Album, AlbumNotFoundError


class GdriveAlbum(Album):

    MIME_FOLDER = 'application/vnd.google-apps.folder'

    _gdrive = None
    _album_id = None

    _folder_details = None
    _content = None

    _albuns = []
    _pictures = []

    def __init__(self, gdrive_service, album_id):
        self._gdrive = gdrive_service
        self._album_id = album_id
        self._load()

    def _load(self):
        try:
            self._folder_details = self._gdrive.files().get(
                fileId=self._album_id).execute()
        except HttpError:
            raise AlbumNotFoundError()

    def load_content(self):
        ITEMS_PER_CALL = 100
        folders = []
        files = []
        param = {}
        while True:
            results = self._gdrive.files().list(
                corpora="user",
                q="parents='%s'" % self._album_id,
                pageSize=ITEMS_PER_CALL,
                spaces='drive',
                fields="nextPageToken, files(id, name, mimeType)",
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