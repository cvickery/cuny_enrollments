#! /usr/local/bin/python3
""" Convert latest Enrollments csv to a web page for Laura.
      Create lists by rd, copt, and w
      Generate web page
"""

import csv
from pathlib import Path
from collections import namedtuple
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-s', '--semester', default='2020.FALL')
args = parser.parse_args()

candidate = sorted(Path('/Users/vickery/CUNY_Enrollments/').glob('*combined*'),
                   reverse=True)[0]
Lists = namedtuple('Lists', 'EC MQR LPS WCGI USED CE IS SW LIT LANG SCI SYN W')
Course = namedtuple('Course', 'title sections enrollment seats rd copts')
Section = namedtuple('Section', 'seats enrollment')
# lists = Lists._make()

courses = dict()
sections = dict()

Row = None
with open(candidate) as infile:
  reader = csv.reader(infile)
  for line in reader:
    if Row is None:
      Row = namedtuple('Row', [c.replace(' ', '_').replace('#', 'num').lower() for c in line])
      row_len = len(Row._fields)
      continue
    if not line[1] != args.semester:
      continue
    while len(line) < row_len:
      line.append('')
    row = Row._make(line)
    if row.course not in courses.keys():
      courses[row.course] = Course._make([row.title, 0, 0, 0, row.rd, row.copt])
    if row.class_num not in sections.keys():
      sections[row.class_num] = {row.course: [0, 0]}
    try:
      sections[row.class_num][row.course][0] += int(row.enrollment)
      sections[row.class_num][row.course][1] += int(row.limit)
    except KeyError as ke:
      print('ke: ',
            row.course,
            row.class_num,
            sections[row.class_num])
      continue
    print(row.course,
          row.class_num,
          sections[row.class_num][row.course][0],
          sections[row.class_num][row.course][1])
print(len(courses), 'courses')
print(len(sections), 'sections')
