#! /usr/local/bin/bash

# Log this execution
echo "$0 on `hostname` at `date`"

if [[ `hostname` =~ cuny.edu ]]
then
  # Get any new course catalog query results, gened course lists, or session dates.
  export LFTP_PASSWORD=`cat /Users/vickery/.lftpwd`
  /usr/local/bin/lftp -f ./getcunyrc
else
  echo Cannot access Tumbleweed from `hostname`
fi

# (re-)generate latest enrollment and gened sheets
./mogrify.py

# (re-)generate the session dates sheet
# ./session_dates.py

# Copy the new files to Google Drive, and archive them
./to_senate_site.py

# Update the lists of scheduled GenEd courses.
./generate_offered.py
