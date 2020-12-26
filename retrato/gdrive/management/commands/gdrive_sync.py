import hashlib
import os
from argparse import ArgumentParser

import rfc3339
from datetime import datetime
import pickle
import json

import PIL.Image
from django.core.management.base import BaseCommand
from django.conf import settings
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from retrato.gdrive.google_auth import create_google_service


class Command(BaseCommand):

    help = 'Synchronize local folder with Google Drive'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--rebuild-tree',
                            action='store_true',
                            help='Rebuild local file tree from Google drive')
        parser.add_argument('--md5',
                            action='store_true',
                            help='Calculate md5 of each file to make the diff')
        parser.add_argument('--skip-cache',
                            action='store_true',
                            help='Skip cache and load the remote content directly')

    def handle(self, *args, **options):
        cache_mngmt = CacheManagement()
        gdrive_synchronizer = GdriveSynchonizer(cache_mngmt)
        gdrive_synchronizer.skip_cache = options['skip_cache']
        gdrive_synchronizer.md5_check = options['md5']
        if options['rebuild_tree']:
            gdrive_synchronizer.rebuild_files_tree_cache()
        else:
            gdrive_synchronizer.sync_all_folders()


class CacheManagement:

    PRIVATE_DIR = os.path.join(settings.BASE_DIR, "private")
    CACHE_TREE_FILE = os.path.join(PRIVATE_DIR, "gdrive_files.pickle")

    def load_files_tree_from_cache(self):
        if not os.path.exists(self.CACHE_TREE_FILE):
            self.rebuild_files_tree_cache()
        with open(self.CACHE_TREE_FILE, "rb") as f:
            print("Loading pickle file '%s'" % self.CACHE_TREE_FILE)
            gdrive_folder_node = pickle.load(f)
        return gdrive_folder_node

    def save_files_tree_to_cache(self, files_tree):
        print("Saving file tree cache to file %s" % self.CACHE_TREE_FILE)
        with open(self.CACHE_TREE_FILE, "wb") as f:
            pickle.dump(files_tree, f, pickle.HIGHEST_PROTOCOL)


class GdriveSynchonizer:

    skip_cache = False
    md5_check = False

    MIME_FOLDER = 'application/vnd.google-apps.folder'

    ITEMS_PER_CALL = 100

    service = None
    cache_mngmt = None

    def __init__(self, cache_mngmt:CacheManagement):
        self.service = create_google_service()
        self.cache_mngmt = cache_mngmt

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

    def create_folder(self, google_folder_node, folder_name):
        print("Creating folder %s/%s" % (google_folder_node.get("name", ""), folder_name))
        file_metadata = {
                        'name': folder_name,
                        'mimeType': GdriveSynchonizer.MIME_FOLDER,
                        'parents': [google_folder_node["id"]]
                    }
        file_node = self.service.files().create(body=file_metadata, fields='id, name').execute()
        return file_node

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
        return dt_taken, dt_modified

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
                                resumable=False)

        if file_id is not None:
            self.service.files().delete(fileId=file_id).execute()

        file_node = self.service \
            .files() \
            .create(body=file_metadata,
                    media_body=media,
                    fields='id, name, md5Checksum').execute()
        return file_node

    def md5(self, filename, blocksize=65536):
        checksum = hashlib.md5()
        with open(filename, "r+b") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                checksum.update(block)
        return checksum.hexdigest()

    def sync_all_folders(self):
        if self.skip_cache:
            gdrive_folder_node = {'id': settings.GDRIVE_ROOT_FOLDER_ID}
        else:
            gdrive_folder_node = self.cache_mngmt.load_files_tree_from_cache()
        (folders_created, files_uploaded) = self.sync_folders(settings.PHOTOS_ROOT_DIR,
                                                              gdrive_folder_node,
                                                              gdrive_folder_node)
        print("%s files uploaded" % files_uploaded)
        if (folders_created + files_uploaded) > 0:
            self.cache_mngmt.save_files_tree_to_cache(gdrive_folder_node)

    def sync_folders(self, source_folder, gdrive_folder_node, gdrive_root_node):
        if self.skip_cache:
            google_items = self.list_google_folder(gdrive_folder_node["id"])
            gdrive_folder_node["files"] = google_items
        else:
            google_items = sorted(gdrive_folder_node["files"], key=lambda item: item["name"])
        local_items = self.list_local_folder(source_folder)

        i_google = 0
        files_uploaded = 0
        folders_created = 0
        dirs_to_process = []
        for item in local_items:
            item_name = item["name"]
            while i_google < len(google_items) and item_name > google_items[i_google]["name"]:
                i_google += 1

            # Skip empty files
            if not item["is_dir"] and os.path.getsize(item["path"]) <= 0:
                continue

            google_item = None
            # Is the file missing?
            if i_google >= len(google_items) or item_name != google_items[i_google]["name"]:
                if item["is_dir"]:
                    new_folder = self.create_folder(gdrive_folder_node, item_name)
                    google_item = {"id": new_folder['id'], "name": item_name, 'files': []}
                    dirs_to_process.append((item["path"], google_item))
                    folders_created += 1
                else:
                    google_item = self.upload_file(gdrive_folder_node["id"], item["path"])
                    files_uploaded += 1
            else:
                google_item = google_items[i_google]
                if item["is_dir"]:
                    dirs_to_process.append((item["path"], google_item))
                elif self.md5_check:
                    # Did the file change?
                    md5sum = self.md5(item["path"])
                    if md5sum != google_item["md5Checksum"]:
                        google_item = self.upload_file(gdrive_folder_node["id"], item["path"], file_id=google_item["id"])
                        files_uploaded += 1
            if google_item is not None:
                gdrive_folder_node['files'].append(google_item)

            if files_uploaded % 10 == 9:
                self.cache_mngmt.save_files_tree_to_cache(gdrive_root_node)

        del google_items
        del local_items

        if files_uploaded > 0:
            self.cache_mngmt.save_files_tree_to_cache(gdrive_root_node)

        for subfolder, google_subfolder_node in dirs_to_process:
            sync_tries = 0
            while sync_tries < 2:
                try:
                    subfolders_created, subfiles_uploaded = self.sync_folders(subfolder,
                                                                              google_subfolder_node,
                                                                              gdrive_root_node)
                    break
                except HttpError as e:
                    sync_tries += 1
                    error_response = json.loads(e.content)
                    # Create directory if it fails because it doesn't exist anymore
                    if error_response.get("error", {}).get("code") == 404:
                        new_folder = self.create_folder(gdrive_folder_node, google_subfolder_node["name"])
                        # Now the directory has a new id
                        google_subfolder_node['id'] = new_folder["id"]
                        # Remove any file that was created previously
                        google_subfolder_node['files'] = []

            folders_created += subfolders_created
            files_uploaded += subfiles_uploaded

        return folders_created, files_uploaded

    def rebuild_files_tree_cache(self):
        print("Rebuilding files tree cache")
        files_tree=self.get_files_tree(settings.GDRIVE_ROOT_FOLDER_ID)
        self.cache_mngmt.save_files_tree_to_cache(files_tree)

    def get_files_tree(self, root_folder_id):
        param = {}
        all_files = []
        root_folder = {"id": root_folder_id, "files": []}
        all_folders = {root_folder_id: root_folder}
        while True:
            while True:
                try:
                    results = self.service.files().list(
                        corpora="user",
                        pageSize=self.ITEMS_PER_CALL,
                        spaces='drive',
                        fields="nextPageToken, files(id, name, parents, mimeType, md5Checksum)",
                        **param).execute()
                    break
                except:
                    print('!', end='', flush=True)
            print('.', end='', flush=True)
            items = results.get('files', [])
            for item in items:
                if item["mimeType"] == self.MIME_FOLDER:
                    if item["id"] == root_folder_id:
                        continue
                    item["files"] = []
                    all_folders[item["id"]] = item
                if 'parents' not in item:
                    continue
                del item['mimeType']
                all_files.append(item)
            if not items or len(items) < self.ITEMS_PER_CALL:
                break
            param['pageToken'] = results.get("nextPageToken")
            if not param['pageToken']:
                break
        print("")
        for item in all_files:
            parent_id = item["parents"][0]
            if parent_id not in all_folders:
                continue
            element = all_folders[parent_id]
            del item["parents"]
            element["files"].append(item)
        return root_folder
