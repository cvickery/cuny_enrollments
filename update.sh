#! /usr/local/bin/bash

# Get any new course catalog query results
export LFTP_PASSWORD=`cat /Users/vickery/.lftpwd`
/usr/local/bin/lftp -f ./getcunyrc
if [[ $? != 0 ]]
then echo 'No new data'
     exit 1
else ./mogrify.py
fi