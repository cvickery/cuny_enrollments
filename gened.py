""" Create a spreadsheet showing Core and College Option coursse at QC.
    The input file for this program is hand-edited from a cuny_courses query:
      copy (select discipline||' '||catalog_number as Course,
      designation, attributes
      from courses
      where institution = 'QNS01'
      and (designation in ('RECR', 'RLPR', 'RMQR', 'FCER', 'FISR', 'FSWR', 'FUSR', 'FWGR')
      or attributes ~ 'QNS')
      order by course) to '/Users/vickery/CUNY_Enrollments/gened.txt'
"""
import csv

pathways = {'RECR': 'EC',
            'RMQR': 'MQR',
            'RLPR': 'LPS',
            'FWGR': 'WCGI',
            'FUSR': 'USED',
            'FCER': 'CE',
            'FISR': 'IS',
            'FSWR': 'SW'
            }

with open('gened.txt', 'r') as infile:
  with open('gened.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Course', 'Core', 'COPT'])
    for line in infile:
      row = line.split()
      row[0] = f'{row[0]} {row[1]}'
      del row[1]
      while len(row) > 3:
        row[2] = f'{row[2]}, {row[3]}'
        del row[3]
      writer.writerow(row)
