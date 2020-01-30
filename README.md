# CUNY Enrollments

Converts a CUNYfirst query, QNS\_CV\_ENROLLMENT\_CAPACITY, and converts it into a CSV file named
*Enrollments\_&lt;term>\_&lt;date>.csv*. The output file gives course title, course components, sections, seats, enrollment limit, number of students enrolled, and the name of the primary instructor for each section, ordered by discipline and catalog number.

- The &lt;term> part of the output file name is generated from the *term* and *session* information
  returned by the query.
- The &lt;date> part of the output file name is the date the query was run on CUNYfirst (reporting
  instance)
- Catalog numbers greater than 1,000 are divided by ten for purposes of ordering courses.
- The current (2020-01-30) version of the query selects only Queens College courses.
