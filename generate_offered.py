#! /usr/local/bin/python3
""" Convert latest Enrollments csv to web pages showing scheduled PLAS and Pathways courses for each
    term not yet completed.

    A separate web page will generate links to each available one.

    The idea is to generate a set of offered_gened pages, indexed by semester.
    That's not what it does right now.
"""

import sys
import csv
from pathlib import Path
from collections import namedtuple, defaultdict
from argparse import ArgumentParser
from datetime import date

from term_codes import term_code, term_code_to_name

parser = ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

requirement_names = {'EC': 'English Composition',
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


# to_html()
# ------------------------------------------------------------------------------------------------
def to_html(semester, info, html_file, asof_date):
  """ Given a dict of titles, rds, and attrbuites indexed by course, generate an HTML report for
      a semester.
  """
  semester_name = term_code_to_name(semester)
  # Generate the list of courses for each requirement
  print(f"""
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8"/>
      <title>{semester} GenEd Courses</title>
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


gen_date = date.today().strftime('%Y-%m-%d')

# Get most-recent available enrollments file
latest_enrollments = None
new_files = Path('./new_files/').glob('*enrollments.csv')
for new_file in new_files:
  if latest_enrollments is None or \
     latest_enrollments.stat().st_mtime < new_file.stat().st_mtime:
     latest_enrollments = new_file

if latest_enrollments is None:
  new_files = Path('./archive/').glob('*enrollments.csv')
  for new_file in new_files:
    if latest_enrollments is None or \
       latest_enrollments.stat().st_mtime < new_file.stat().st_mtime:
       latest_enrollments = new_file

if latest_enrollments is None:
  sys.exit('No enrollments file available')
else:
  print(f'Using {latest_enrollments.resolve()}')
  asof_date = date.fromtimestamp(latest_enrollments.stat().st_mtime)
  asof_date_str = asof_date.strftime('%B %d, %Y')

# Pull enrollment info for all scheduled gened courses
headings = None
gened_courses = defaultdict(list)
with open(latest_enrollments) as csv_file:
  reader = csv.reader(csv_file)
  for line in reader:
    if headings is None:
      headings = [h.lower().replace(' ', '_').replace('?', '').replace('#', 'num') for h in line]
      Row = namedtuple('Row', headings)
      continue
    row = Row._make(line)
    if row.gened_rd != '' or row.gened_attribute != '':
      gened_courses[row.semester_code].append(row)

# Process offerings in semester order
for semester in sorted(gened_courses.keys()):
  with open(f'./offered_gened/{semester}.html', 'w') as html_file:
    offered_pathways_courses = defaultdict(set)
    courses = sorted(gened_courses[semester], key=lambda row: (row.gened_rd,
                                                               row.gened_attribute,
                                                               row.course))
    course_info = dict()
    for course in courses:
      course_str = course.course.strip()
      if course_str not in course_info.keys():
        course_info[course_str] = {'title': course.title,
                                   'sections': 0,
                                   'limit': 0,
                                   'enrollment': 0}
        course_info[course_str]['sections'] += 1
        course_info[course_str]['limit'] += int(course.limit)
        course_info[course_str]['enrollment'] += int(course.enrollment)
        if course.gened_rd != '':
          offered_pathways_courses[course.gened_rd].add(course_str)
        copts = course.gened_attribute.split(',')
        for copt in [c.strip() for c in copts]:
          if copt != '':
            offered_pathways_courses[copt.strip()].add(course_str)

    # Generate the html file
    semester_name = term_code_to_name(semester)
    print(f"""
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8"/>
      <title>{semester} GenEd Courses</title>
      <style>
        body {{
          padding: 1em;
        }}
        .course-list {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            column-gap: 1em;
            row-gap: 0;
        }}
        .course-list h2 {{
          grid-column-start: 1;
          grid-column-end: 4;
          grid-row-start: 1;
          grid-row-end:2;
        }}
        .note {{
          font-weight:normal;
          font-size:1em;
        }}
        .course-list p {{
          margin:0;
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
      <p><em>CUNYfirst data as of {asof_date}</em></p><hr>

  """, file=html_file)

    for requirement in pathways_requirements:
      suffix = '' if len(offered_pathways_courses[requirement]) == 1 else 's'
      if requirement == 'EC':
        note = ('<br/><span class="note"Note: English Composition requires two courses, which are'
                ' called College Writing 1 (ENGL 110) and College Writing 2 at Queens College'
                '</span>')
      else:
        note = ''
      print(f'<section class="course-list">'
            f'<h2>{requirement_names[requirement]} '
            f'(<em>{len(offered_pathways_courses[requirement])}'
            f' course{suffix}</em>){note}</h2>', file=html_file)
      for course in sorted(offered_pathways_courses[requirement]):
        title = course_info[course]['title']
        num_sections = course_info[course]['sections']
        suffix = '' if num_sections == 1 else 's'
        enrollment = course_info[course]['enrollment']
        limit = course_info[course]['limit']
        try:
          per_cent = f'({100 * enrollment / limit:.0f}% filled)'
        except ZeroDivisionError:
          per_cent = ''
        print(f'<p><strong>{course}</strong> {title}: <em>{num_sections} section{suffix}; '
              f'{enrollment:,} / {limit:,} seats {per_cent}</em>', file=html_file)
      print("""
          </section><hr>
        </body>
      </html>
      """, file=html_file)

# print(f"""
#     </section>
#     <h1>Perspectives Offerings for {semester_name}</h1>
#     <p><em>CUNYfirst data as of {asof_date}</em></p>
#     <hr>
#     <section class="course-list">
# """, file=html_file)
# for requirement in plas_requirements:
#   print(f'<h2>{Requirements[requirement]} (<em>{len(offered_plas_courses[requirement])}'
#         f' courses</em>)</h2>', file=html_file)
#   for course in sorted(offered_plas_courses[requirement]):
#     title = all_courses[course].title
#     num_sections = len(all_courses[course].sections)
#     suffix = '' if num_sections == 1 else 's'
#     enrollment = all_courses[course].data[0]
#     limit = all_courses[course].data[1]
#     try:
#       per_cent = f'({100 * enrollment / limit:.0f}%)'
#     except ZeroDivisionError:
#       per_cent = ''
#     print(f'<p>{course} {title}<span class="stats">: <em>{num_sections} section{suffix}; '
#           f'{enrollment:,} / {limit:,} seats {per_cent} filled</em></span>', file=html_file)
