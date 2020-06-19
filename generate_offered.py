#! /usr/local/bin/python3
""" Convert latest Enrollments csv to web pages showing scheduled PLAS and Pathways courses for each
    term not yet completed.
    The idea is to generate a set of offered_gened pages, indexed by semester.
    That's not what it does right now.
"""

import sys
import csv
from pathlib import Path
from collections import namedtuple
from argparse import ArgumentParser
from datetime import date

from term_codes import term_code

parser = ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-s', '--session', default='1')
parser.add_argument('-t', '--term', default='1202')
args = parser.parse_args()

gen_date = date.today().strftime('%Y-%m-%d')
code, semester, semester_name = term_code(args.term, args.session)
html_file = open(f'offered_gened_{semester}_as_of_{gen_date}.html', 'w')

enrollment_file = sorted(Path('/Users/vickery/CUNY_Enrollments/archive').glob('*enrollments.csv'),
                         reverse=True)[0]
asof_date = enrollment_file.name[0:10]
asof_date_str = date.fromisoformat(asof_date).strftime('%B %d, %Y')
gened_file = sorted(Path('/Users/vickery/CUNY_Enrollments/archive').glob('(*gened.csv'),
                    reverse=True)[0]
session_dates_file = sorted(Path('/Users/vickery/CUNY_Enrollments/archive').glob('(*dates.csv'),
                            reverse=True)[0]

Requirements = {'EC': 'English Composition',
                'MQR': 'Mathematics and Quantitative Reasoning',
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
      if args.debug:
        print(Row._fields, file=sys.stderr)
      continue
    if line[1] != semester:
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

    # Update Pathways dicts
    if row.rd in pathways_requirements:
      offered_pathways_courses[row.rd].add(row.course)
    for attr in row.gened_attributes.split(','):
      attr = attr.strip()
      if attr in pathways_requirements:
        offered_pathways_courses[attr].add(row.course)
      if attr in plas_requirements:  # WRIC will match here
        offered_plas_courses[attr].add(row.course)

    # Update PLAS dicts
    if row.course in all_plas_courses.keys():
      for req in all_plas_courses[row.course]:
        offered_plas_courses[req].add(row.course)

# Generate the list of courses for each requirement
print(f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{semester_name} GenEd Courses {asof}</title>
    <style>
      body {{
        padding: 1em;
      }}
      .course-list {{
          column-count: 3;
          column-gap: 1em;
          column-rule: 1px solid #ccc;
      }}
      h1, h1+p {{
        text-align:center;
        margin: 0;
      }}
      @media print {{
        h1:not(:first-of-type) {{
          page-break-before: always;
        }}

        h2 {{
          break-after: avoid;
        }}

        .course-list, p {{
          font-size: 8pt;
        }}
      }}
    </style
  </head>
  <body>
    <h1>Pathways Offerings for {semester_name}</h1>
    <p><em>CUNYfirst data as of {asof_date}</em></p>
    <hr>
    <section class="course-list">
""", file=html_file)
for requirement in pathways_requirements:
  print(f'<h2>{Requirements[requirement]} (<em>{len(offered_pathways_courses[requirement])}'
        f' courses</em>)</h2>', file=html_file)
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
          f'{enrollment:,} / {limit:,} seats {per_cent} filled</em></span>', file=html_file)

print(f"""
    </section>
    <h1>Perspectives Offerings for {semester_name}</h1>
    <p><em>CUNYfirst data as of {asof_date}</em></p>
    <hr>
    <section class="course-list">
""", file=html_file)
for requirement in plas_requirements:
  print(f'<h2>{Requirements[requirement]} (<em>{len(offered_plas_courses[requirement])}'
        f' courses</em>)</h2>', file=html_file)
  for course in sorted(offered_plas_courses[requirement]):
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
          f'{enrollment:,} / {limit:,} seats {per_cent} filled</em></span>', file=html_file)
print("""
    </section>
  </body>
</html>
""", file=html_file)