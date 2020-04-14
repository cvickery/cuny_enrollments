#! /usr/local/bin/python3
""" Upload all csv files in the "new_files" folder to the archives folder on Google Drive, and move
    them to the archive folder here.
      Based on sample code from developer.google.com/
      I don't know what command line arguments are supported by oauth2client.tools.

    The client_id.json file, which is kept outside the project, identifies the developer (Vickery).
    The first time the program runs on a computer, it will open a browser window where the user
    must agree to grant access to the program to update their Google Drive. If the user is not
    Vickery, this means setting up a folder to receive the uploads and copying the id of that folder
    into the 'parents' line below.
    (The client_id.json file has to be kept secret so that a malicious user doesn't use it to sign
    a malicious app.)

"""
import sys
from pathlib import Path
import argparse

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

archive_dir_id = '1wpTfVy7MF4Y7ds1mNfUO2eLxInrMHhmQ'
combined_sheet_id = '1g36HsFjtf-_emG_4t36HF7S8O1TMS7AsvYBoPUeIiOY'

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('/Users/vickery/Google/client_id.json', scope=SCOPES)
    creds = tools.run_flow(flow, store, flags)
service = build('drive', 'v3', http=creds.authorize(Http()))

# The 'new_files' and 'archive' directories are subdirectories of my 'CUNY_Enrollments' project dir.
proj_dir = '/Users/vickery/CUNY_Enrollments'
from_dir = f'{proj_dir}/new_files'
to_dir = f'{proj_dir}/archive'

# Get all the csv files in the new_files directory
new_files = [file for file in Path(from_dir).glob('*.csv')]
if len(new_files) == 0:
  sys.exit('No new files to upload.')

# Upload each new file to Google Drive
for new_file in new_files:
  file_metadata = {
      'name': new_file.name,
      'parents': [archive_dir_id],  # id of my Google Drive archives folder
      'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert csv to Google Sheet on upload
  }
  file_name = f'{from_dir}/{new_file.name}'
  result = service.files().create(body=file_metadata, media_body=file_name).execute()
  print(f'Uploaded {new_file.name}')

  # If this is a "combined" enrollments sheet, update the contents of "latest_enrollments_combined"
  if 'combined' in new_file.name:
    # File's new content.
    media_body = MediaFileUpload(new_file.resolve(),
                                 mimetype='application/vnd.google-apps.spreadsheet',
                                 resumable=True)
    # Do the update
    result = service.files().update(fileId=combined_sheet_id,
                                    media_body=media_body).execute()
    print(f'Uploaded {new_file.resolve()} to {result["name"]}')

  # And move it to the archive folder.
  new_file.rename(f'{to_dir}/{new_file.name}')
