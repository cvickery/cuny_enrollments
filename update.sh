#! /usr/local/bin/bash

# Get any new course catalog query results
export LFTP_PASSWORD=`cat /Users/vickery/.lftpwd`
/usr/local/bin/lftp -f ./getcunyrc

# (re-)generate latest sheet
./mogrify.py
