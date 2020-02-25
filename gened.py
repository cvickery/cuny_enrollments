#! /usr/local/bin/python3
""" Create a spreadsheet showing Core and College Option courses at QC.
"""
import csv
import re
import sys

from pathlib import Path
from collections import namedtuple

# Dictionary of CF RDs used at QC and their abbreviations
rds = {'RECR': 'EC',
       'RLPR': 'LPS',
       'RMQR': 'MQR',
       'FCER': 'CE',
       'FISR': 'IS',
       'FUSR': 'USED',
       'FSWR': 'SW',
       'FWGR': 'WGCI'}

GenEd = namedtuple('GenEd', 'rd copt')
geneds = dict()


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


# Get latest  QNS_GENED csv from downloads and say that that's that.
that = None
them = Path().glob('./downloads/*GENED*.csv')
for this in them:
  if that is None or this.stat().st_mtime > that.stat().st_mtime:
    that = this
if that is None:
  sys.error('No input file found')
try:
  print(f'Using {that.name}')
  with open(that) as gened_file:
    cols = None
    reader = csv.reader(gened_file)
    for line in reader:
      if cols is None:
        cols = ([col.lower().replace(' ', '_') for col in line])
        GenEd_Row = namedtuple('GenEd_Row', cols)
      else:
        row = GenEd_Row._make(line)
        sysdate = row.sysdate
        course = f'{row.subject.strip()} {row.catalog.strip()}'
        if row.designation in rds.keys():
          rd = rds[row.designation]
        else:
          rd = '—'
        copts = [copt for copt in row.copt.split(', ') if copt.startswith('QNS')]
        if len(copts) == 0:
          copts = ['—']
        geneds[course] = [rd, ', '.join(copts)]
  courses = sorted(geneds.keys(), key=lambda c: numeric_part(c))
  courses = sorted(courses, key=lambda c: discipline_part(c))

  # Generate the CSV output file.
  outfile_name = f'Gened_{sysdate}.csv'
  print(f'Generating {outfile_name}')
  with open(outfile_name, 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Course', 'Core', 'COPT'])
    for course in courses:
      writer.writerow([course] + geneds[course])

except Exception as e:
  print('*** Error:', e)
