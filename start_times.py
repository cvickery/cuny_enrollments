#! /usr/local/bin/python3
""" Give CSV file with frequencies of the hours in which class sections start, by day of week at QC
    for the past year.
    Things that could/should be added:
      * Pay attention to semester or class component.
      * Add other colleges, which would require an expanded CF query to be added to the mix.
      * Don't hard-code the query set, currently the one generated for September 5, 2020.
"""
import codecs
import csv
from collections import namedtuple, defaultdict

from term_codes import term_code

day_names = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
institutions = ['BAR01', 'BCC01', 'BKL01', 'BMC01', 'CSI01', 'CTY01', 'HOS01', 'HTR01', 'JJC01',
                'KCC01', 'LAG01', 'LEH01', 'MEC01', 'NCC01', 'NYT01', 'QCC01', 'QNS01', 'YRK01']
cols = None
start_times = defaultdict(int)  # key by day of (week, hour)
with codecs.open('/Users/vickery/Desktop/QCCV_SR_CLASSES_ALL-41450350.csv',
                 'r', encoding='utf-8', errors='replace') as infile:
    reader = csv.reader(infile)
    for line in reader:
      if cols is None:
        line[0] = line[0].replace('\ufeff', '')
        if line[0] != 'Institution':
          continue
        cols = [col.lower().replace(' ', '_') for col in line]
        Row = namedtuple('Row', cols)
      else:
        row = Row._make(line)
        if row.institution not in institutions or (row.term != '1209'):
          continue
        try:
          code, name, string = term_code(row.term, row.session)
        except (ValueError, AssertionError):
          pass
        for day_name in day_names:
          if line[cols.index(day_name)] and line[cols.index('meeting_time_start')]:
            start_times[(string,
                         row.institution,
                         day_names.index(day_name),
                         row.meeting_time_start[0:2])] += 1

print('Term, College, Day, Hour, Freq')
for key in sorted(start_times.keys()):
  print(f' {key[0]}, {key[1]}, {day_names[key[2]]}, {key[3]}, {start_times[key]}')
