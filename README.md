# CUNY Enrollments

A script, *update.sh* generates three files with information about enrollments and approved GenEd courses derived from CUNYfirst queries, which run daily.

## Enrollments
Convert a CUNYfirst query, QCCV\_SR\_ENRL\_LOC\_TIME\_RD, into CSV files named
*Enrollments_&lt;date>.combined.csv* and *Enrollments_&lt;date>.separate.csv*. The output files give enrollment, scheduling, and other information about all scheduled courses as of the date indicated. The difference between the two files is whether the class meeting schedule is shown in (up to) three columns for three class meetings per week, or in a more compact for combining all class meeeting times into one column.

- The output files contain information for all semesters starting within the previous year and continuing forward. During enrollment periods, this information will change day-to-day for those semester open for enrollment.
- As enrollment periods roll over, new semesters are automatically added to the output.
- In the output file, the semester is given in two equivalent formats: YYYY.&lt;*code*> and YYYY.&lt;*abbr*>
    - YYYY is the calendar year
    - &lt;*code*> is the CUNYfirst "session code" for the semester
    - &lt;*abbr*> uses these abbreviations for the semester names:
        - SPR Spring
        - FALL Fall
        - WIN Winter
        - SS1 Summer Short I
        - SS2 Summer Short II
        - SL1 Summer Long I
        - SL2 Summer Long II
        - S10 Summer 10 Weeks

    - Catalog numbers greater than 1,000 are divided by ten for purposes of ordering courses.

## GenEd

The query *QNS\_GENED* gives the Requirement Designation (RD) and Course Attributes for all Queens College courses. The *gened.py* script turns this into a list of all courses where the RD is Pathways "Common Core" designation or any of the attributes are for Queens' "College Option" requirements. The output file is named *Gened\_&lt;date>.csv*.

Although GenEd requirements don't change often, this table is updated daily anyway.

## Update.sh

This is the script that gets the CUNYfirst query outputs from Tumbleweed, and (re-)generates the three output files, using the latest versions of the CUNYfirst queries available.

- The "-sd" ("skip download") command line option suppresses the download from Tumbleweed in case the query files are available by some means other than download from Tumbleweed. (Used for development.)
- Uses the *mogrify.py* script to generate the Enrollment files.
- Uses the *gened.py* script to generate the Gened file.