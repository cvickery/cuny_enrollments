#! /usr/local/bin/python3
""" Convert latest Enrollments csv to a web page showing scheduled PLAS and Pathways courses.
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

enrollment_file = sorted(Path('/Users/vickery/CUNY_Enrollments/archive').glob('*combined*'),
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

Course = namedtuple('Course', 'title sections data')

# Offered courses
offered_pathways_courses = {req: set() for req in pathways_requirements}
offered_plas_courses = {req: set() for req in plas_requirements}

# All PLAS courses
all_plas_courses = dict()

# Populate all_plas_courses
with open('./plas.csv') as plas_file:
  reader = csv.reader(plas_file)
  header = None
  for line in reader:
    if header is None:
      header = line
    else:
      course, plas_requirement = line
      if course not in all_plas_courses.keys():
        all_plas_courses[course] = []
      all_plas_courses[course].append(plas_requirement)

# Gather information for all sections of all scheduled courses
all_courses = dict()
requirements = {r: {} for r in Requirements.keys()}
Row = None
with open(enrollment_file) as infile:
  reader = csv.reader(infile)
  for line in reader:
    if Row is None:
      Row = namedtuple('Row', [c.replace(' ', '_').replace('#', 'num').lower() for c in line])
      row_len = len(Row._fields)
      continue
    if line[1] != code:
      continue
    while len(line) < row_len:
      line.append('')
    row = Row._make(line)
    if row.course not in all_courses.keys():
      all_courses[row.course] = Course._make([row.title, set(), [0, 0]])
    if row.section not in all_courses[row.course].sections:
      all_courses[row.course].sections.add(row.section)
    all_courses[row.course].data[0] += int(row.enrollment)
    all_courses[row.course].data[1] += int(row.limit)

    if row.rd in pathways_requirements:
      offered_pathways_courses[row.rd].add(row.course)
    for attr in row.attr.split(','):
      attr = attr.strip()
      if attr in pathways_requirements:
        offered_pathways_courses[attr].add(row.course)

# Generate the list of courses for each requirement
print(f'<h1>Pathways Offerings for {semester_name}')
for requirement in pathways_requirements:
  print(f'<h2>{Requirements[requirement]} (<em>{len(offered_pathways_courses[requirement])} '
        f'courses</em>)</h2>')
  for course in sorted(offered_pathways_courses[requirement]):
    title = all_courses[course].title
    num_sections = len(all_courses[course].sections)
    suffix = '' if num_sections == 1 else 's'
    enrollment = all_courses[course].data[0]
    limit = all_courses[course].data[1]
    try:
      per_cent = f'({100 * enrollment / limit:.0f}%)'
    except ZeroDivisionError:
      per_cent = ''
    print(f'<p>{course} {title}<span class="stats">: <em>{num_sections} section{suffix}; '
          f'{enrollment:,} / {limit:,} seats {per_cent} filled</em></span>')

print(f'<h1>Perspectives Offerings for {semester_name}')
for requirement in plas_requirements:
  print(f'<h2>{Requirements[requirement]}</h2>')

# print(len(courses), 'courses')
# print('----------------------------------------------')
# print(requirements)
# print('----------------------------------------------')
# print(courses)
