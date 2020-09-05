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

day_names = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
cols = None
start_times = defaultdict(int)  # key by day of (week, hour)
with codecs.open('downloads/QCCV_SR_CLASS_ENRL_LOC_TIME_RD-41345176.csv',
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
        for day_name in day_names:
          if line[cols.index(day_name)] and line[cols.index('meeting_time_start')]:
            start_times[(day_names.index(day_name),
                         line[cols.index('meeting_time_start')][0:2])] += 1

print('Day, Hour, Freq')
for key in sorted(start_times.keys()):
  print(f'{day_names[key[0]]}, {key[1]}, {start_times[key]}')
