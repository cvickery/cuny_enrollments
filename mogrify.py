#! /usr/local/bin/python3
""" Transform CUNY enrollment query into something useful.
"""

import sys
import csv
import codecs
import re

from datetime import date
from typing import Dict, Any
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

from term_codes import term_code

csv.field_size_limit(sys.maxsize)

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def numeric_part(catnum_str):
  num_part = float(re.search(r'(\d+(\.\d+)?)', catnum_str).group(1))
  while num_part > 1000.0:
    num_part /= 10.0
  return f'{num_part:06.1f}'


def make_meetings_str(start, end, days_yn):
  """ Make a string that tells the days and times when a class section meets.
      Spaces are filled with @, which need to be fixed once the string has been encapsulated in
      a cell.
  """
  day_list = set()
  for i in range(len(days_yn)):
    if days_yn[i] == 'Y':
      day_list.add(i)
  days_str = ',@'.join([days[index] for index in sorted(day_list)])
  return (f'{start.replace(":00.000000", "").strip()}'
          f'—{end.replace(":00.000000", "").strip()}@{days_str}')


def mogrify(input_file):
  """
  """
  input_path = Path(input_file)
  if not input_path.exists():
    raise ValueError(f'{input_path} not found.')

  courses = []
  status_counts: Dict[str, int] = dict()
  cols = None
  term = None

  # with open(input_file, 'r') as f:
  #   decrufted = f.read().translate(cruft_table)

  # with io.StringIO(decrufted) as infile:
  with codecs.open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
    reader = csv.reader(infile)
    for line in reader:
      if cols is None:
        line[0] = line[0].replace('\ufeff', '')
        if line[0] != 'Institution':
          continue
        cols = [col.lower().replace(' ', '_') for col in line]
        if args.debug:
          print(cols, file=sys.stderr)
        Row = namedtuple('Row', cols)
      else:
        row = Row._make(line)
        if row.institution != 'QNS01':
          continue
        if term is None:
          code, term = term_code(row.term, row.session)
          m, d, y = row[-1].split('/')
          file_name = f'Enrollments_{y}-{m}-{d}_{term}.csv'
        if row.class_status not in status_counts.keys():
          status_counts[row.class_status] = 0
        status_counts[row.class_status] += 1
        if row.class_status != 'Active':
          continue
        course_str = f'{row.subject_area:>7}@{row.catalog_nbr.strip():<6}'
        title = row.class_title.replace(' ', '@').replace('\'', '’')
        section = row.section
        class_number = row.class_nbr
        component = row.course_component
        enrollment = row.total_enrollment
        limit = row.enrollment_capacity
        room = row.facil_id
        mode = row.mode
        meetings_str = make_meetings_str(row.mtg_start, row.mtg_end,
                                         [row.mon, row.tues, row.wed, row.thurs,
                                          row.fri, row.sat, row.sun])

        # For spaces in the instructor’s name
        instructor = row.instructor.replace(',', ',@').replace(' ', '@')
        courses.append(f'{course_str} {title} {class_number} {section:>05} {component} {limit:>4} '
                       f'{enrollment:>3} {room} {meetings_str} {mode} {instructor}')
  courses.sort(key=lambda course: numeric_part(course[8:14]))
  courses.sort(key=lambda course: course[0:7].strip())
  with open(file_name, 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Course', 'Title', 'Class #', 'Section', 'Component', 'Limit', 'Enrollment',
                     'Room', 'Schedule', 'Mode', 'Instructor'])
    for course in courses:
      row = course.split()
      row = [col.replace('@', ' ') for col in row]
      writer.writerow(row)

  for status, count in status_counts.items():
    print(f'{count:6,} {status}', file=sys.stderr)


if __name__ == '__main__':
  parser = ArgumentParser(description='Transform CUNY enrollment query into something useful.')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-q', '--query_file', default=None)
  args = parser.parse_args()
  if args.query_file is None:
    that = None
    # Get latest csv from downloads and say that that's that.
    them = Path().glob('./downloads/*.csv')
    for this in them:
      if that is None or this.stat().st_mtime > that.stat().st_mtime:
        that = this
  else:
    that = Path(args.query_file)
  print(f'Using {that.name}')
  mogrify(that)

