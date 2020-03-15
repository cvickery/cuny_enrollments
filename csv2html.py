#! /usr/local/bin/python3
""" Convert latest Enrollments csv to a web page for Laura.
      Create lists by rd, copt, and w
      Generate web page
"""

import csv
from pathlib import Path
from collections import namedtuple
from argparse import ArgumentParser
from term_codes import term_code

parser = ArgumentParser()
parser.add_argument('-t', '--term', default='1202')
parser.add_argument('-s', '--session', default='1')
args = parser.parse_args()

semester, code, semester_name = term_code(args.term, args.session)

source_csv = sorted(Path('/Users/vickery/CUNY_Enrollments/archive').glob('*combined*'),
                    reverse=True)[0]
Requirements = {'EC': 'English Composition',
                'MQR': 'Mathematics and Quatnitative Reasoning',
                'LPS': 'Life and Physical Sciences',
                'WCGI': 'World Cultures and Global Issues',
                'USED': 'United States Experience in its Diversity',
                'CE': 'Creative Expression',
                'IS': 'Individual and Society',
                'SW': 'Scientific World',
                'QNSLIT': 'QC Literature',
                'QNSLANG': 'QC Language',
                'QNSSCI': 'QC Science',
                'QNSSYN': 'QC Synthesis',
                'WRIC': 'Writing Intensive',
                'AP': 'Appreciating and Participating in the Arts',
                'CV': 'Culture and Values',
                'NS': 'Natural Science',
                'NS+L': 'Natural Science with Laboratory',
                'RL': 'Reading Literature',
                'SS': 'Analyzing Social Structures',
                'US': 'United States',
                'ET': 'European Traditions',
                'WC': 'World Cultures',
                'PI': 'Pre-Industrial Society'}
pathways_requirements = ['EC', 'MQR', 'LPS',
                         'WCGI', 'USED', 'CE', 'IS', 'SW',
                         'QNSLIT', 'QNSLANG', 'QNSSCI', 'QNSSYN', 'WRIC']
plas_requirements = ['AP', 'CV', 'NS', 'NS+L', 'RL', 'SS', 'US', 'ET', 'WC', 'PI', 'WRIC']

Course = namedtuple('Course', 'title sections data rd attrs')

# Gather information for all sections of all scheduled courses
courses = dict()
requirements = {r: {} for r in Requirements.keys()}
Row = None
with open(source_csv) as infile:
  reader = csv.reader(infile)
  for line in reader:
    if Row is None:
      Row = namedtuple('Row', [c.replace(' ', '_').replace('#', 'num').lower() for c in line])
      row_len = len(Row._fields)
      continue
    if line[1] != semester:
      continue
    while len(line) < row_len:
      line.append('')
    row = Row._make(line)
    if row.course not in courses.keys():
      courses[row.course] = Course._make([row.title, set(), [0, 0], row.rd, row.attr])
    if row.section not in courses[row.course].sections:
      courses[row.course].sections.add(row.section)
      courses[row.course].data[0] += int(row.enrollment)
      courses[row.course].data[1] += int(row.limit)
      if row.rd in requirements.keys():
        requirements[row.rd][row.course] = courses[row.course]
      for attr in row.attr.split(','):
        attr = attr.strip()
        if attr in requirements.keys():
          requirements[attr][row.course] = courses[row.course]
# Generate the list of courses for each requirement
print(f'<h1>Pathways Offerings for {semester_name}')
for requirement in pathways_requirements:
  print(f'<h2>{Requirements[requirement]}</h2>')
  for course in courses:
    print(course)
print(f'<h1>Perspectives Offerings for {semester_name}')
for requirement in plas_requirements:
  print(f'<h2>{Requirements[requirement]}</h2>')

# print(len(courses), 'courses')
# print('----------------------------------------------')
# print(requirements)
# print('----------------------------------------------')
# print(courses)
