#! /usr/local/bin/python3
""" Transform QCCV_SR_CLASS_ENRL_LOC_TIME_RD into something useful.
"""

import csv
import codecs
import os
import re
import sys

from datetime import date
from typing import Dict, List, Tuple, Any
from argparse import ArgumentParser
from collections import namedtuple, defaultdict
from pathlib import Path

from term_codes import term_code

# Side effect of importing from the gened module is to generate a new gened.csv file.
from gened import gened_courses, rds, GenEd

csv.field_size_limit(sys.maxsize)

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Generate dict of GenEd courses and the requirements they satisfy
no_gened = GenEd._make(['', '', '', ''])

ClassInfo = namedtuple('ClassInfo', 'semester_code semester_name course_str title career has_fees '
                                    'is_ztc primary_component this_component class_number '
                                    'class_status section enrollment limit schedule mode '
                                    'instructor rd variant attr class_notes')


def instructor_order(arg):
  """  Name (role)
       Return a string that orders the role PI->Si->TA->other, followed by the name.
  """
  role = 9  # No role or role not in {PI, SI, TA}
  matches = re.match(r'.*?\((.*)\)', arg)
  if matches:
    try:
      role = ['PI', 'SI', 'TA'].index(matches.group(1))
    except ValueError:
      pass
  return f'{role}{arg}'


def numeric_part(catnum_str):
  """ For sorting courses in catalog number order within a discipline.
  """
  num_part = float(re.search(r'(\d+(\.\d+)?)', catnum_str).group(1))
  while num_part > 1000.0:
    num_part /= 10.0
  return f'{num_part:06.1f}'


def make_meetings_str(room, start, end, days_yn):
  """ Make a string that tells the days and times when a class section meets.
      Spaces are filled with @, which need to be fixed once the string has been encapsulated in
      a cell.
  """
  room_str = f'{room}: ' if room != '' else room
  day_list = set()
  for i in range(len(days_yn)):
    if days_yn[i] == 'Y':
      day_list.add(i)
  if len(day_list) > 0:
    dows = [days[index] for index in sorted(day_list)]
    time = (f'{start.replace(":00.000000", "").strip().lower()}-'
            f'{end.replace(":00.000000", "").strip().lower()}')
    return f'{room_str}' + ', '.join(dows) + f' {time.replace(" ", " ")}'
  else:
    return ''


def mogrify(input_file, separate_meeting_cols=False):
  """ Convert an ENROLLMENT-CAPACITY query into a useable format, including GenEd info.
  """
  input_path = Path(input_file)
  if not input_path.exists():
    raise ValueError(f'{input_path} not found.')

  # A class is identified by the term and class_number. If the class meets in different rooms and/or
  # has more than one instructor, there will be multiple rows returned by the CF query, which have
  # to be combined to avoid over-counting enrollments.
  classes: Dict[Tuple, List] = dict()

  # Report only Active classes, but count others.
  status_counts = defaultdict(int)

  cols = None
  outfile = None
  # Force the input file to be valid utf-8 text.
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
        # The CUNYfirst query could be used for any institution, but this is a QC project.
        if row.institution != 'QNS01':
          continue

        # Use the SYSDATE from the first data row to build the output file name
        if outfile is None:
          # Use the query SYSDATE for the output file name
          m, d, y = (int(col) for col in row.sysdate.split('/'))
          # Depending on how the query is run, the year might be 2 digits. Assume 21st century.
          if y < 100:
            y += 2000
          outfile = Path(f'./new_files/{y}-{int(m):02}-{int(d):02}_enrollments.csv')

        semester_code, semester_name, semester_string = term_code(row.term, row.session)
        # Count Cancelled, Stop Enrollment, and Tentative items, but process only Active.
        class_status = row.class_status
        status_counts[class_status] += 1
        # if row.class_status != 'Active':
        #   continue
        course_str = f'{row.subject_area:>7} {row.catalog_nbr.strip():<6}'
        title = row.class_title.replace('\'', '’')
        career = row.career
        primary_component = row.primary_component
        has_fees = row.fees_exist if row.fees_exist == 'Y' else ''
        is_ztc = 'Y' if 'OERS' in row.attributes else ''
        section = row.class_section
        class_number = row.class_nbr
        this_component = row.course_component
        if this_component == 'MSG':
          continue

        enrollment = row.enrollment_total
        limit = row.enrollment_capacity
        mode = row.instruction_mode
        class_notes = row.class_notes
        schedule = make_meetings_str(row.room,
                                     row.mtg_start,
                                     row.mtg_end,
                                     [row.mon,
                                      row.tues,
                                      row.wed,
                                      row.thurs,
                                      row.fri,
                                      row.sat,
                                      row.sun])
        gened_key = course_str.strip()
        if gened_key in gened_courses.keys():
          gened = gened_courses[gened_key]
        else:
          gened = no_gened

        instructor = row.instructor.replace(',', ', ') if row.instructor != '' else 'Unknown'
        role = f' ({row.role})' if row.role != '' else ''
        instructor += role
        class_key = (semester_code, class_number)
        if class_key not in classes.keys():
          classes[class_key] = ClassInfo._make([semester_code,
                                                semester_name,
                                                course_str,
                                                title,
                                                career,
                                                has_fees,
                                                is_ztc,
                                                primary_component,
                                                this_component,
                                                class_number,
                                                class_status,
                                                section,
                                                enrollment,
                                                limit,
                                                [schedule],
                                                mode,
                                                [instructor],
                                                gened.rd,
                                                gened.variant,
                                                gened.attr.replace('@', ' '),
                                                class_notes])
        else:
          # Check that everything except instructors/rooms is the same
          if args.debug:
            new_data = [semester_code,
                        semester_name,
                        course_str,
                        title,
                        career,
                        has_fees,
                        is_ztc,
                        primary_component,
                        this_component,
                        class_number,
                        class_status,
                        section,
                        enrollment,
                        limit,
                        [schedule],
                        mode,
                        [instructor],
                        gened.rd,
                        gened.variant,
                        gened.attr,
                        class_notes]
            for old, new in zip(classes[class_key], new_data):
              if old != new:
                print(class_key, old, new)
          if schedule not in classes[class_key].schedule:
            classes[class_key].schedule.append(schedule)
          if instructor not in classes[class_key].instructor:
            classes[class_key].instructor.append(instructor)
  # classes.sort(key=lambda course: numeric_part(course[8:14]))
  # classes.sort(key=lambda course: course[0:7].strip())
  archive_file = Path('./archive', outfile.name)
  if archive_file.exists() and not os.getenv('DEVELOPMENT'):
    print(f'mogrify.py: {archive_file} already exists', file=sys.stderr)
  else:
    print(f'Generating {outfile}')
    with open(outfile, 'w') as csv_file:
      writer = csv.writer(csv_file)
      writer.writerow(['Semester Code', 'Semester Name',
                       'Course', 'Title', 'Level', 'Has Fees?', 'OERS?', 'Primary Component',
                       'This Component', 'Class #', 'Class Status', 'Section', 'Enrollment',
                       'Limit', 'Schedule', 'Mode', 'Instructor', 'GenEd RD', 'STEM Variant?',
                       'GenEd Attribute', 'Class Notes'])
      for row in classes:
        cells = list(classes[row])
        for i in range(len(cells)):
          if isinstance(cells[i], list):
            cells[i] = '\n'.join(sorted(cells[i], key=lambda cell: instructor_order(cell)))
        writer.writerow(cells)

    for status, count in status_counts.items():
      print(f'{count:6,} {status}', file=sys.stderr)


if __name__ == '__main__':
  """ Find the latest enrollment file and process it.
  """
  parser = ArgumentParser(description='Transform CUNY enrollment query into something useful.')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-q', '--query_file', default=None)
  parser.add_argument('-sv', '--stem_variant', action='store_true')
  args = parser.parse_args()
  if args.query_file is None:
    that = None
    # Get latest csv from downloads and say that that's that.
    them = Path().glob('./downloads/QCCV_SR_CLASS_ENRL_LOC_TIME_RD*.csv')
    for this in them:
      if that is None or this.stat().st_mtime > that.stat().st_mtime:
        that = this
  else:
    that = Path(args.query_file)
  print(f'Using {that.name}')
  mogrify(that)
