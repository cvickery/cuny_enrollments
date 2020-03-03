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
  # Get any new course catalog query results
  export LFTP_PASSWORD=`cat /Users/vickery/.lftpwd`
  /usr/local/bin/lftp -f ./getcunyrc
fi

# (re-)generate latest sheet, with separate meeting day columns
./mogrify.py -s
./mogrify.py
