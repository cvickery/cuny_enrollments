#! /usr/bin/env python3
""" Generate a dict of STEM courses (designation is MQR, LPS, or SW).
    Mark the designation of each course that has more than 3 contact hours or 3 credits with an
    asterisk. These, presumably. are STEM variants.
"""
from pgconnection import PgConnection


conn = PgConnection()
cursor = conn.cursor()
cursor.execute(f"""select discipline,
                          catalog_number,
                          contact_hours, min_credits,
                          designation,
                          case
                            when contact_hours > 3 or min_credits >3 then '*'
                            else ''
                            end as "sv"
                     from cuny_courses
                     where institution = 'QNS01'
                     and course_status = 'A'
                     and designation in ('RMQR', 'RLPR', 'FSWR')
                     and discipline !~ '^[FR]C..$'
                     order by designation, discipline, numeric_part(catalog_number)
                     """)

stem_designations = {f'{r.discipline} {r.catalog_number}': f'{r.designation}{r.sv}'
                     for r in cursor.fetchall()}
if __name__ == '__main__':
  for course, designation in stem_designations.items():
    print(f'{course:<12} {designation}')
