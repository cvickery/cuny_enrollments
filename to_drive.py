#! /usr/local/bin/python3
from pathlib import Path

from googleapiclient import discovery, http
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('/Users/vickery/Google/client_id.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

new_files = Path('./new').glob('*')
for new_file in new_files:
  print(new_file.name)
  file_metadata = {
      'name': new_file.name,
      'mimeType': 'application/vnd.google-apps.spreadsheet'
  }

  # This part doesn't work yet.
  media = http.MediaFileUpload(new_file,
                               mimetype='text/csv',
                               resumable=True)
  file = drive_service.files().create(body=file_metadata,
                                      media_body=new_file.read_text(),
                                      fields='id').execute()
