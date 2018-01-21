from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
import httplib2
import json
from apiclient import discovery

def save_credentials(credentials):
    storage = Storage(credential_file)
    storage.put(credentials)


def refresh_token(credentials):
    credentials.refresh(httplib2.Http())
    save_credentials(credentials)


auth_base_folder = '/Users/r.paiva/projects/WerneckPaiva/retrato/private/'
client_secret_filename = auth_base_folder + 'client_secret.json'
credential_file = auth_base_folder + "credentials.dat"

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
service = discovery.build('drive', 'v3', http=http)

folder_id = "1toZLDXAabgTBauntnd4Y0y90kW0_aR44"
folder = service.files().get(fileId=folder_id).execute()

param = {}
for i in range(10):
    # results = service.files().list(
    #     corpora="user",
    #     q="parents='%s' and mimeType='image/jpeg'" % folder_id,
    #     pageSize=100,
    #     spaces='drive',
    #     fields="nextPageToken, files(id, name, size, thumbnailLink)", # , imageMediaMetadata
    #     **param).execute()

    results = service.files().list(
        corpora="user",
        q="parents='%s' and mimeType='application/vnd.google-apps.folder'" % '1GcNdNdjkgaoO243ILUD-C2BMwBmmtRYi',
        pageSize=100,
        spaces='drive',
        fields="nextPageToken, files(id, name, parents)",
        **param).execute()

    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            # metadata = service.files().get(fileId=item['id'], alt="media").execute()
            # print('{0} ({1})'.format(item['name'], item['id']))
            # print(metadata)
            print(item)
    param['pageToken'] = results.get("nextPageToken")
    if (not param['pageToken']):
        break