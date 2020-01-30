#! /usr/local/bin/python3

from argparse import ArgumentParser

months = ['Zero', 'January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
def term_code(term:str, session:str) -> str:
  """ Convert CUNYfirst term code (CYYM) and session code (1, WIN, 4W1, etc) into a QC term_code,
      YYYYTTTT.
       cyymmm Name            Abbreviation
          010 Winter          Win
          020 Spring          Spr
          041 Summer 1 short  S1s
          042 Summer 1 long   S1l
          061 Summer 2 short  S2s
          062 Summer 2 long   S2l
          009 Fall            Fall
          003, 004, 005, etc. Mon(th)
  """
  year = 1900 + 100 * int(term[0]) + int(term[1:3])
  month = f'0{term[3]}'

  if session == '1':
    term_code = f'{year}{month}0'
    if month == '02':
      term_name = f'Spring {year}'
    elif month == '09':
      term_name = f'Fall {year}'
    else:
      # Probably Summer Session, but just use the month name
      term_name = f'{months[int(month, 16)]} {year}'

  elif session == 'WIN':
    # CUNYfirst used to associate Winter with previous Fall (9 for the month). In that case add 1
    # to the year.
    if month == '09':
      year += 1
    term_code = f'{year}010'  # January
    term_name = f'Winter {year}'

  elif session == '4W1':
    term_code = f'{year}041'
    term_name = f'Summer Short I {year}'

  elif session == '4W2':
    term_code = f'{year}042'
    # This code changed meaning in 2016
    if year < 2016:
      term_name = f'Summer Long I {year}'
    else:
      term_name = f'Summer Short II {year}'

  elif session == '10W':
  # Another change in 2016: this was a ten-week summer session that wasn’t intended to be used,
  # but CHEM 113 does use it.
    term_code = f'{year}060'
    term_name = f'Summer Ten Week {year}'

  elif session == '6W1':
    term_code = f'{year}061'
    term_name = f'Summer Long I {year}'

  elif session == '6W2':
    term_code = f'{year}062'
    term_name = f'Summer Long II {year}'

  else:
    raise ValueError(f'Unknown session code: {session}')

  return term_code, term_name

if __name__ == '__main__':
  parser = ArgumentParser(description='Convert CUNYfirst term and session into term_code.')
  parser.add_argument('-d', '--debug', action='store_true')
  parser.add_argument('-t', '--term', default='1202')
  parser.add_argument('-s', '--session', default='1')
  args = parser.parse_args()
  if args.debug:
    print(f'{args.term} {args.session} => ', end='')
  term_code, term_name = term_code(args.term, args.session)
  # print(f'{float(term_code)/10:.1}', term_name)
  print(f'{float(term_code)/10:.1f}', term_name)

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
