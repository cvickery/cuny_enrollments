#! /usr/local/bin/bash

#  Command line args (lifted from CUNY_Curriculum/update_db)
while [ $# -gt 0 ]
  do
    if [[ ( "$1" == "--interactive" ) || ( "$1" == '-i' ) ]]
    then progress='--progress'
         report='--report'
    elif [[ ( "$1" == "--no-events" ) || ( "$1" == "-ne" ) ]]
    then no_events=1
    elif [[ ( "$1" == "--skip-download") || ( "$1" == "-sd" ) ]]
      then skip_download=1
    elif [[ ( "$1" == "--no-size-check") || ( "$1" == "-ns" ) ]]
      then no_size_check=1
    elif [[ ( "$1" == "--no-date-check") || ( "$1" == "-nd" ) ]]
      then no_date_check=1
    elif [[ ( "$1" == "--no-archive") || ( "$1" == "-na" ) ]]
      then no_archive=1
    elif [[ ( "$1" == "--no-programs" ) || ( "$1" == "-np" ) ]]
      then no_programs=1
    else
      echo "Usage: $0 [-ne | --no-events] [-ns | --no-size-check] [-nd | --no-date-check]
       [-na | --no-archive] [-sd | --skip_download] [-np | --no_programs] [-i | --interactive]"
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
./gened.py
