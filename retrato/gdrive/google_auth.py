from os import path
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
import httplib2
from apiclient import discovery
import json
from django.conf import settings

auth_base_folder = path.join(settings.BASE_DIR, "private")
client_secret_filename = path.join(auth_base_folder, 'client_secret.json')
credential_file = path.join(auth_base_folder, "credentials.dat")

def save_credentials(credentials):
    storage = Storage(credential_file)
    storage.put(credentials)

def refresh_token(credentials):
    credentials.refresh(httplib2.Http())
    save_credentials(credentials)

gdrive_service = None

def create_google_service():
    global gdrive_service
    if gdrive_service is None:
        if not path.exists(client_secret_filename):
            raise Exception("Could not find file %s" % client_secret_filename)

        app_client_secret = json.load(open(client_secret_filename))["installed"]
        flow = OAuth2WebServerFlow(client_id=app_client_secret["client_id"],
                                   client_secret=app_client_secret["client_secret"],
                                   scope='https://www.googleapis.com/auth/drive',
                                   redirect_uri='http://localhost/return',
                                   access_type='offline',
                                   prompt="consent")

        storage = Storage(credential_file)
        credentials = storage.get()
        if not credentials or credentials.invalid:
            class MyOpts:
                pass
            flags=MyOpts()
            flags.logging_level = 'DEBUG'
            flags.noauth_local_webserver = False
            flags.auth_host_port = [8100]
            flags.auth_host_name = 'localhost'
            credentials = tools.run_flow(flow, storage, flags=flags)

        if credentials.access_token_expired:
            refresh_token(credentials)


        http = credentials.authorize(httplib2.Http())
        gdrive_service = discovery.build('drive', 'v3', http=http)

    return gdrive_service