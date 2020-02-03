# CUNY Enrollments

Converts a CUNYfirst query, QNS\_CV\_ENROLLMENT\_CAPACITY, and converts it into a CSV file named
*Enrollments_&lt;date>_&lt;term>.csv*. The output file gives course title, course components,
sections, seats, enrollment limit, number of students enrolled, and the name of the primary
instructor for each section, ordered by discipline and catalog number.

- The &lt;term> part of the output file name is generated from the *term* and *session* information
  returned by the query. It has the four-digit calendar year, a dot, and a two-digit term code,
  which has numerical values that increase during the year so that a set if saved files will be in
  chronological order when listed by filename.
- The &lt;date> part of the output file name is the date the query was run on CUNYfirst (reporting
  instance)
- Catalog numbers greater than 1,000 are divided by ten for purposes of ordering courses.
- The current (2020-01-30) version of the query selects only Queens College courses.
