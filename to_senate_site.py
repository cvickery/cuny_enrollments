#! /usr/local/bin/python3
""" This script was previously called "to_drive.py" because it was used to build an archive of QC
    enrollment data on Google Drive. It also did updated GenEd information for the
    senate.qc.cuny.edu/Curriculum website. Now that QC has abandoned Google Drive (July 2022), that
    part of the code has been amputated, but the senate website update remains.

    Old Comments:
    -------------
    Upload all csv files in the "new_files" folder to the archives folder on Google Drive, and move
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

    Update: 2020-05-29
    When there is a new gened csv, copy it to the old Senate website.
"""
import sys
from pathlib import Path
import argparse

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools

# Get all the csv files in the new_files directory

# The 'new_files' and 'archive' directories are subdirectories of my 'CUNY_Enrollments' project dir.
proj_dir = '/Users/vickery/Projects/cuny_enrollments'
from_dir = f'{proj_dir}/new_files'
to_dir = f'{proj_dir}/archive'

new_files = [file for file in Path(from_dir).glob('*.csv')]
if len(new_files) == 0:
  sys.exit('No new files.')

# Check for gened.csv
for new_file in new_files:
  if new_file.name.endswith('gened.csv'):
    target = Path('/Users/vickery/Sites/senate.qc.cuny.edu/'
                  'Curriculum/Approved_Courses/gened_courses.csv')
    target.unlink(missing_ok=True)
    target.hardlink_to(new_file)
    print(f'Linked {new_file.name} to Senate website as {target.name}')
  # Move all new files to the archive folder.
  new_file.rename(f'{to_dir}/{new_file.name}')

# Now that QC Google Accounts are gone, the rest of this won’t work.
exit()

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

archive_dir_id = '1wpTfVy7MF4Y7ds1mNfUO2eLxInrMHhmQ'
latest_enrollments_id = '1g36HsFjtf-_emG_4t36HF7S8O1TMS7AsvYBoPUeIiOY'
session_dates_id = '1YxcGZuGi5MS8SFSQ2iQ23SpNLVQKRlnvrF2onNkEPT8'

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('/Users/vickery/Projects/Google_qc/client_id.json',
                                          scope=SCOPES)
    creds = tools.run_flow(flow, store, flags)
service = build('drive', 'v3', http=creds.authorize(Http()))

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

  # If this is an enrollments sheet, update the contents of "latest_enrollments"
  if 'enrollments' in new_file.name:
    # File's new content.
    media_body = MediaFileUpload(new_file.resolve(),
                                 mimetype='application/vnd.google-apps.spreadsheet',
                                 resumable=True)
    # Do the update
    result = service.files().update(fileId=latest_enrollments_id,
                                    media_body=media_body).execute()
    print(f'Updated {result["name"]} from {new_file.name}')

  # If this is a session dates sheet, update the contents of "session_dates"
  if 'session' in new_file.name:
    # File's new content.
    media_body = MediaFileUpload(new_file.resolve(),
                                 mimetype='application/vnd.google-apps.spreadsheet',
                                 resumable=True)
    # Do the update
    result = service.files().update(fileId=session_dates_id,
                                    media_body=media_body).execute()
    print(f'Updated {result["name"]} from {new_file.name}')

