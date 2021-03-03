#! /usr/local/bin/bash

#  Command line args (lifted from CUNY_Curriculum/update_db)
while [ $# -gt 0 ]
  do
    if [[ ( "$1" == "--skip-download") || ( "$1" == "-sd" ) ]]
      then skip_download=1
    else
      echo "Usage: $0 [-sd | --skip_download]"
      exit 1
    fi
    shift
  done

if [[ ! $skip_download ]]
then
  # Get any new course catalog query results, gened course lists, or session dates.
  export LFTP_PASSWORD=`cat /Users/vickery/.lftpwd`
  /usr/local/bin/lftp -f ./getcunyrc
fi

# Piggyback transfers applied query: move to ../transfers_applied project
mv downloads/CV_QNS_TRNS_DTL* ../transfers_applied/downloads

# (re-)generate latest enrollment and gened sheets
./mogrify.py

# (re-)generate the session dates sheet
./session_dates.py

# Copy the new files to Google Drive, and archive them
./to_drive.py

# Update the lists of scheduled GenEd courses.
./generate_offered.py
