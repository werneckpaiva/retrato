import hashlib
import os
import time
import rfc3339
from datetime import datetime

import PIL.Image
from django.core.management import BaseCommand
from django.conf import settings
from googleapiclient.http import MediaFileUpload

from retrato.gdrive.google_auth import create_google_service


class Command(BaseCommand):

    help = 'Synchronize local folder with Google Drive'

    def handle(self, *args, **options):
        gdrive_synchronizer = GdriveSynchonizer()
        (folders_created, files_uploaded) = gdrive_synchronizer.sync_folders(settings.PHOTOS_ROOT_DIR, settings.GDRIVE_ROOT_FOLDER_ID)
        print("Files uploaded: %s" % files_uploaded)


class GdriveSynchonizer:


    MIME_FOLDER = 'application/vnd.google-apps.folder'

    service = None

    def __init__(self):
        self.service = create_google_service()

    def list_google_folder(self, folder_id):
        ITEMS_PER_CALL = 100
        all_items = []
        param = {}
        while True:
            results = self.service.files().list(
                corpora="user",
                # q="parents='%s' and mimeType='application/vnd.google-apps.folder'" % '1GcNdNdjkgaoO243ILUD-C2BMwBmmtRYi',
                # q="parents='%s' and properties has { key='backup' and value='true' }" % FOLDER_ID,
                q="parents='%s'" % folder_id,
                pageSize=ITEMS_PER_CALL,
                spaces='drive',
                fields="nextPageToken, files(id, name, parents, mimeType, md5Checksum)",
                **param).execute()

            items = results.get('files', [])
            all_items = all_items + items
            if not items or len(items) < ITEMS_PER_CALL:
                break

            param['pageToken'] = results.get("nextPageToken")
            if (not param['pageToken']):
                break
        all_items = sorted(all_items, key=lambda x: x["name"])
        return all_items

    def list_local_folder(self, folder_path):
        all_names = os.listdir(folder_path)
        all_items = []
        for name in all_names:
            file_path = os.path.join(folder_path, name)
            all_items.append({
                "name": name,
                "is_dir": os.path.isdir(file_path),
                "path": file_path
            })

        all_items = sorted(all_items, key=lambda x: x["name"])
        return all_items

    def create_folder(self, google_folder_id, folder_name):
        file_metadata = {
                        'name': folder_name,
                        'mimeType': GdriveSynchonizer.MIME_FOLDER,
                        'parents': [google_folder_id]
                    }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        folder_id = file.get('id')
        return folder_id

    def get_taken_and_modified_time(self, file_path):
        try:
            img = PIL.Image.open(file_path)
            exif_data = img._getexif()
            str_dt_taken = exif_data.get(306, None)
            dt_taken = datetime.strptime(str_dt_taken, "%Y:%m:%d %H:%M:%S")
        except:
            dt_taken = ""
        if not dt_taken:
            dt_taken = datetime.fromtimestamp(os.path.getctime(file_path))

        dt_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        return (dt_taken, dt_modified)

    def upload_file(self, google_folder_id, path, file_id=None):
        print("Uploading file %s" % path)
        (dt_taken, dt_modified) = self.get_taken_and_modified_time(path)
        file_name = os.path.basename(path)
        file_metadata = {
            'name': file_name,
            'parents': [google_folder_id],
            'createdTime': rfc3339.rfc3339(dt_taken),
            'modifiedTime': rfc3339.rfc3339(dt_modified)
        }

        if file_name.lower().endswith(".jpg"):
            mimetype = 'image/jpeg'
        else:
            mimetype = None
        media = MediaFileUpload(path,
                                mimetype=mimetype,
                                resumable=True)

        if (file_id is not None):
            self.service.files().delete(fileId=file_id).execute()

        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        file_id = file.get("id")
        return file_id

    def md5(self, filename, blocksize=65536):
        checksum = hashlib.md5()
        with open(filename, "r+b") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                checksum.update(block)
        return checksum.hexdigest()

    def sync_folders(self, source_folder, google_folder_id):
        print("Sync %s" % source_folder)
        google_items = self.list_google_folder(google_folder_id)
        local_items = self.list_local_folder(source_folder)

        i_google = 0
        files_uploaded = 0;
        folders_created = 0;
        dirs_to_process = []
        for item in local_items:
            item_name = item["name"]
            while i_google < len(google_items) and item_name > google_items[i_google]["name"]:
                i_google += 1

            # Is file empty?
            if not item["is_dir"] and os.path.getsize(item["path"]) <= 0:
                continue

            # Is the file missing?
            if i_google >= len(google_items) or item_name != google_items[i_google]["name"]:
                if item["is_dir"]:
                    new_folder_id = self.create_folder(google_folder_id, item_name)
                    dirs_to_process.append((item["path"], new_folder_id))
                    folders_created += 1
                else:
                    self.upload_file(google_folder_id, item["path"])
                    files_uploaded += 1
            else:
                google_item = google_items[i_google]
                if item["is_dir"]:
                    dirs_to_process.append((item["path"], google_item["id"]))
                else:
                    # Did the file change?
                    md5sum = self.md5(item["path"])
                    if (md5sum != google_item["md5Checksum"]):
                        self.upload_file(google_folder_id, item["path"], file_id=google_item["id"])
                        files_uploaded += 1


        del google_items
        del local_items

        for (subfolder, google_subfolder_id) in dirs_to_process:
            (subfolders_created, subfiles_uploaded) = self.sync_folders(subfolder, google_subfolder_id)
            folders_created += subfolders_created
            files_uploaded += subfiles_uploaded

        return (folders_created, files_uploaded)

