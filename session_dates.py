#! /usr/local/bin/python3

import csv
from collections import namedtuple
from datetime import date
from pathlib import Path

from term_codes import term_code

# Module initialization: get end dates for terms so they can be looked up by end_date()
# SIDE EFFECT: generate session_dates.csv for uploading to Google Drive
session_table_query_file = None
end_dates = {}
session_table_query_files = Path('./downloads/').glob('QNS_CV_SESSION_TABLE*')
last_mod_time = 0.0
for sess_tab_qf in session_table_query_files:
  mtime = sess_tab_qf.stat().st_mtime
  if mtime > last_mod_time:
    last_mod_time = mtime
    session_table_query_file = sess_tab_qf

if session_table_query_file is not None:
  new_file = Path('./new_files/session_dates.csv')
  with open(new_file, 'w') as session_dates:
    session_dates.write('term_code\tsession_start_date\tsession_end_date\t'
                        'enroll_start_date\tenroll_end_date\tweeks\tcensus_date\n')
    with open(session_table_query_file, 'r') as csv_file:
      csv_reader = csv.reader(csv_file)
      cols = None
      for line in csv_reader:
        if cols is None:
          cols = [col.lower().replace(' ', '_') for col in line]
          Cols = namedtuple('Cols', cols)
          continue
        row = Cols._make(line)
        try:
          code, name, string = term_code(row.term, row.session)
          end_dates[code] = row.session_end_date
          session_dates.write(f'{code}\t{row.session_beginning_date}\t{row.session_end_date}\t'
                              f'{row.first_date_to_enroll}\t{row.last_date_to_enroll}\t'
                              f'{row.weeks_of_instruction}\t{row.census_date}\n')
          sys_date = row.sysdate
        except ValueError:
          pass
    m, d, y = (int(x) for x in sys_date.split('/'))
    new_file.rename(Path(new_file.parent, date(y, m, d).strftime('%Y-%m-%d_') + new_file.name))


def end_date(term_code: str) -> date:
  """ Given a term_code, return its session_end_date.
  """
  if session_table is None:
    raise ValueError('Session Table not available')
  return end_dates(term_code)
