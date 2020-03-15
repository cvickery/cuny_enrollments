#! /usr/local/bin/python3

import codecs
import csv

from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path


def term_code(term: str, session: str) -> str:
  """ Convert CUNYfirst term code (CYYM) and session code (1, WIN, 4W1, etc) into a QC term_code
      string, YYYY.TT, and term name. The idea is that the term code strings are in chronological
      order.
      C is the century: 0 for 1900's and 1 for 2000's
      YY is the year in the century
      M is a month number, interpretation depends on session code (SSS)


   M  SSS   TT Name             Abbr
   2* WIN   10 Winter           WIN
   2    1   20 Spring           SP
   6  4W1   41 Summer 1 Short   SS1
   6  4W2   42 Summer 1 Long    SL1
   6  10W   60 Summer 10 Week   S10
   6  6W1   61 Summer 2 Short   SS2
   6  6W2   62 Summer 2 Long    SL2
   9    1   90 Fall             FA
  """
  year = 1900 + 100 * int(term[0]) + int(term[1:3])
  month = f'{term[3]}'

  if session == '1':
    term_code = f'{year}.{month}0'
    if month == '2':
      term_name = f'{year}.SPR'
      term_string = f'Spring {year}'
    elif month == '9':
      term_name = f'{year}.FALL'
      term_string = f'Fall {year}'
    else:
      raise ValueError(f'Unknown term-session: {term}-{session}')

  elif session == 'WIN':
    # *CUNYfirst used to associate Winter with previous Fall (9 for the month). In that case add 1
    # to the year.
    if month == '9':
      year += 1
    term_code = f'{year}.10'
    term_name = f'{year}.WIN'
    term_string = f'Winter {year}'

  elif month == '6' and session == '4W1':
    term_code = f'{year}.41'
    term_name = f'{year}.SS1'
    term_string = f'Summer Short I {year}'

  elif month == '6' and session == '4W2':
    term_code = f'{year}.042'
    # This code changed meaning in 2016
    if year < 2016:
      term_name = f'{year}.SL1'
      term_string = f'Summer Long I {year}'
    else:
      term_name = f'{year}.SS2'
      term_string = f'Summer Short II {year}'

  elif month == '6' and session == '10W':
    # Another change in 2016: this was a ten-week summer session that wasn’t intended to be used,
    # but CHEM 113 does use it.
    term_code = f'{year}.60'
    term_name = f'{year},S10'
    term_string = f'Summer 10 Week {year}'

  elif month == '6' and session == '6W1':
    term_code = f'{year}.61'
    term_name = f'{year}.SL1'
    term_string = f'Summer Long I {year}'

  elif month == '6' and session == '6W2':
    term_code = f'{year}.62'
    term_name = f'{year}.SL2'
    term_string = f'Summer Long II {year}'

  else:
    raise ValueError(f'Unknown term-session: {term}-{session}')

  return term_code, term_name, term_string


if __name__ == '__main__':

  TermSess = namedtuple('TermSess', 'term session')
  parser = ArgumentParser(description='Convert CUNYfirst term and session into term_code.')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-t', '--term', default='1202')
  parser.add_argument('-s', '--session', default='1')
  parser.add_argument('-f', '--file', default=None)
  args = parser.parse_args()
  if args.file is not None:
    ts_set = set()
    if args.file == 'latest':
      that = None
      them = Path().glob('./downloads/QCCV_SR_CLASS_ENRL_LOC_TIME_RD*.csv')
      for this in them:
        if that is None or this.stat().st_mtime > that.stat().st_mtime:
          that = this
    else:
      that = Path(args.query_file)
    print(f'Using {that}')
    cols = None
    with codecs.open(that, 'r', encoding='utf-8', errors='replace') as infile:
        reader = csv.reader(infile)
        for line in reader:
          if cols is None:
            line[0] = line[0].replace('\ufeff', '')
            if line[0] != 'Institution':
              continue
            cols = [col.lower().replace(' ', '_') for col in line]
            if args.debug:
              print(cols, file=sys.stderr)
            Row = namedtuple('Row', cols)
          else:
            row = Row._make(line)
            ts = (row.term, row.session)
            if ts not in ts_set:
              ts_set.add((row.term, row.session))
              code, name, string = term_code(row.term, row.session)
              print(f'{row.term} {row.session:>3} : {code:8} : {name:9} : "{string}"')
  else:
    code, name, string = term_code(args.term, args.session)
    print(f'{args.term} {args.session:>3} : {code:8} : {name:9} : "{string}"')

""" Above is based on the following extract from get_805_enrollments.php
"""
# $year = 1900 + 100 * substr($cf_term, 0, 1) + substr($cf_term, 1, 2);
# $month = '0'.substr($cf_term, 3, 1);
# switch ($cf_sess)
# {
#   case '1':
#     //  Regular Session (Spring or Fall)
#     $term = $year.$month.'0';
#     if ($month === '02')
#     {
#       $term_name = 'Spring '  . $year;
#       $term_abbr = 'Spr'      . substr($year, 2,  2);
#     }
#     else if ($month === '09')
#     {
#       $term_name = 'Fall '  . $year;
#       $term_abbr = 'Fall'   . substr($year, 2,  2);
#     }
#     else
#     {
#       //  Probably Summer Session, but just give the month
#       $term_name = $months[-1 + $month] . ' '. $year;
#       $term_abbr = substr($months[-1 + $month], 0, 3)
#           . substr($year, 2, 2);
#     }
#     break;
#   case 'WIN':
#     if ($month === '09') $year++;
#     $term = $year . '010';
#     $term_name = 'Winter ' . $year;
#     $term_abbr = 'Win' . substr($year, 2,  2);
#     break;
#   case '4W1':
#     $term = $year . '041';
#     $term_name = "Summer 1 short $year";
#     $term_abbr = 'S1s' . substr($year, 2,  2);
#     break;
#   case '4W2':
#     $term = $year . '042';
#     // This code changed meaning in 2016
#     if ($year < 2016)
#     {
#       $term_name = "Summer 1 long $year";
#       $term_abbr = 'S1l' . substr($year, 2, 2);
#     }
#     else
#     {
#       $term_name = "Summer 2 short $year";
#       $term_abbr = 'S2s' . substr($year, 2, 2);
#     }
#     break;
#   case '10W':
#     // Another change in 2016: a ten-week summer session that wasn't intended to be used, but
#     // CHEM 113 does use it.
#     $term = $year . '060';
#     $term_name = "Summer 10 week $year";
#     $term_abbr = 'S10' . substr($year, 2, 2);
#     break;
#   case '6W1':
#     $term = $year . '061';
#     $term_name = "Summer 2 short $year";
#     $term_abbr = 'S2s' . substr($year, 2, 2);
#     break;
#   case '6W2':
#     $term = $year . '062';
#     $term_name = "Summer 2 long $year";
#     $term_abbr = 'S2l' . substr($year, 2, 2);
#     break;
#   default:
#     //  Pending knowledge of all possible session codes, default to
#     //  using the month, as in the regular session case (1) above.
#     $term = $year.$month.'0';
#     $term_name = $months[-1 + $month] . ' '. $year;
#     $term_abbr = substr($months[-1 + $month], 0, 3)
#         . substr($year, 2, 2);
#     //die("Bad switch on $cf_sess\n");
#     break;
# }
