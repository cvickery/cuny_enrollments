#! /usr/local/bin/python3
""" Create a spreadsheet showing Core and College Option gened_courses at QC.
"""
import csv
import re
import sys
import codecs

from pathlib import Path
from collections import namedtuple
from datetime import date

# Dictionary of CF RDs used at QC and their abbreviations
rds = {'RECR': 'EC',
       'RLPR': 'LPS',
       'RMQR': 'MQR',
       'FCER': 'CE',
       'FISR': 'IS',
       'FUSR': 'USED',
       'FSWR': 'SW',
       'FWGR': 'WCGI'}

all_courses = dict()
GenEd = namedtuple('GenEd', 'rd variant attr')
gened_courses = dict()  # courses with a GenEd RD or Attribute


def numeric_part(arg):
  """ Extract the numeric part of a catalog_number; scale it to range {0.0 : 999.0}
  """
  part = re.search(r'\d+\d?\d*', arg)
  part = float(part.group(0))
  while part > 999:
    part = part / 10
  return part


def discipline_part(arg):
  """ Extract the discipline name from a course_string
  """
  part = re.search(r'\s*(\S+)', arg)
  return part.group(1)


# Get latest courses sheet, and extract info by course_id
that = None
them = Path().glob('./downloads/QNS_GENED_COURSES*.csv')
for this in them:
  if that is None or this.stat().st_mtime > that.stat().st_mtime:
    that = this
if that is None:
  sys.exit('No courses file found')
print(f'Using {that.name}')
with codecs.open(that, 'r', encoding='utf-8', errors='replace') as gened_file:
  cols = None
  reader = csv.reader(gened_file)
  for line in reader:
    if cols is None:
      cols = ([col.lower().replace(' ', '_') for col in line])
      Row = namedtuple('Row', cols)
    else:
      row = Row._make(line)
      sysdate = row.sysdate
      course = f'{row.subject.strip()} {row.catalog.strip()}'
      if course.startswith('RC') or course.startswith('FC'):
        # Ignore exemption pseudo-courses
        continue
      rd = '@'
      stem_variant = '@'
      if row.designation in rds.keys():
        rd = rds[row.designation]
        if float(row.min_units) > 3:
           stem_variant = 'Y'
      course_id = int(row.course_id)
      # print(f'{course_id:06}, {course} {rd}')
      all_courses[course_id] = [course, rd, stem_variant, '']

# Get latest attr sheet, and extract info by course_id
that = None
them = Path().glob('./downloads/QNS_GENED_ATTR*.csv')
for this in them:
  if that is None or this.stat().st_mtime > that.stat().st_mtime:
    that = this
if that is None:
  sys.exit('No attr file found')
print(f'Using {that.name}')
with codecs.open(that, 'r', encoding='utf-8', errors='replace') as gened_file:
  cols = None
  reader = csv.reader(gened_file)
  for line in reader:
    if cols is None:
      cols = ([col.lower().replace(' ', '_') for col in line])
      Row = namedtuple('Row', cols)
    else:
      row = Row._make(line)
      course_id = int(row.course_id)
      attrs = row.attr_value.replace('COPT, ', '').replace('COPT', '').strip()
      try:
        all_courses[course_id][3] = attrs
      except KeyError as ke:
        continue  # inactive
for key in all_courses.keys():
  course, rd, variant, attr = all_courses[key]
  if rd != '@' or attr != '':
    gened_courses[course] = GenEd._make([rd, variant, attr.replace(' ', '@')])

courses = sorted(gened_courses.keys(), key=lambda c: numeric_part(c))
courses = sorted(courses, key=lambda c: discipline_part(c))

# Generate the CSV output file.
m, d, y = (int(x) for x in sysdate.split('/'))
date_str = date(y, m, d).strftime('%Y-%m-%d')
outfile_name = f'./archive/{date_str}_gened.csv'
print(f'Generating {outfile_name}')
with open(outfile_name, 'w') as outfile:
  writer = csv.writer(outfile)
  writer.writerow(['Course', 'Core', 'STEM Variant', 'ATTR'])
  for course in courses:
    writer.writerow([course] + [ge.replace('@', ' ') for ge in gened_courses[course]])
