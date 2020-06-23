#! /usr/local/bin/python3

import codecs
import csv

from argparse import ArgumentParser
from collections import namedtuple
from datetime import date
from pathlib import Path

_sessions = {'10': ('1', 'WIN'),  # WIN
             '20': ('2', '1'),    # SPR
             '58': ('6', '1'),    # Summer 8 Week
             '56': ('6', '2'),    # Summer 6 Week
             '41': ('6', '4W1'),  # Summer 8 Week
             '42': ('6', '4W2'),  # Summer 8 Week
             '60': ('6', '10W'),  # Summer 8 Week
             '61': ('6', '6W1'),  # Summer 8 Week
             '62': ('6', '6W2'),  # Summer 8 Week
             '90': ('9', '1'),    # FALL
             }


def term_code(term: str, session: str) -> tuple:
  """ Convert CUNYfirst term code (CYYM) and session code (1, WIN, 4W1, etc) into a QC term_code
      string "YYYY.TT", and term name string, "YYYY.Abbr". The idea is that the term code strings
      are in chronological order but the term name strings are more descriptive.

      C is the century: 0 for 1900's and 1 for 2000's
      YY is the year in the century
      M is a month number, interpretation depends on session code (SSS)


   M  SSS  Full Name       TT  Abbr
   2* WIN  Winter          10  WIN
   2    1  Spring          20  SPR
   6    1  Summer 8 Week   58  S08 # Used prior to 2009
   6    2  Summer 6 Week   56  S06 # Used prior to 2009
   6  4W1  Summer 1 Short  41  SS1
   6  4W2  Summer 1 Long   42  SL1
   6  10W  Summer 10 Week  60  S10
   6  6W1  Summer 2 Short  61  SS2
   6  6W2  Summer 2 Long   62  SL2
   9    1  Fall            90  FALL
   *CUNYfirst used to associate Winter with previous Fall (9 for the month). In that case add 1
   to the year.
  """
  year = 1900 + 100 * int(term[0]) + int(term[1:3])
  month = f'{term[3]}'

  if session == '1':
    term_code = f'{year}.{month}0'
    if month == '2':
      term_name = f'{year}.SPR'
      term_string = f'Spring {year}'
    elif month == '6':
      term_code = f'{year}.58'
      term_name = f'{year}.S08'
      term_string = f'Summer Long {year}'
    elif month == '9':
      term_name = f'{year}.FALL'
      term_string = f'Fall {year}'
    else:
      raise ValueError(f'Unknown term-session: {term}-{session}')

  elif session == '2':
    assert(month == '6' and year < 2010)
    term_code = f'{year}.56'
    term_name = f'{year}.S06'
    term_string = f'Summer Short {year}'

  elif session == 'WIN' or session == 'MIN':  # Typo for term 1079
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
    term_code = f'{year}.42'
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
    term_name = f'{year}.S10'
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

  return (term_code, term_name, term_string)


# term_code_to_name()
# -------------------------------------------------------------------------------------------------
def term_code_to_name(arg: str) -> str:
  """ Given a term_code as defined above, return the corresponding term_string. Reverse-convert the
      term_code into a CUNYfirst term and session, then use term_code to get the string.
  """
  year, session_code = arg.split('.')
  century = 0 if int(year) < 2000 else 1
  cyy = f'{century}{year[2:4]}'
  month, session = _sessions[session_code]
  code, name, string = term_code(f'{cyy}{month}', session)
  return string


if __name__ == '__main__':

  TermSess = namedtuple('TermSess', 'term session')
  parser = ArgumentParser(description='Convert CUNYfirst term and session into term_code.')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-t', '--term', default='1202')
  parser.add_argument('-s', '--session', default='1')
  args = parser.parse_args()
  code, name, string = term_code(args.term, args.session)
  print(f'{args.term} {args.session:>3} : {code:8} : {name:9} : "{string}"')
  assert string == term_code_to_name(code), f'"{string}" is not "{term_code_to_name(code)}"'
  print('OK')

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
