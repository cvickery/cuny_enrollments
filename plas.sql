-- Get list of approved PLAS courses and their designations from the curric db
copy (
select m.discipline||' '||m.course_number as course,
       -- string_agg(t.abbr, ' ' order by t.abbr) as plas
       t.abbr as plas
 from course_designation_mappings m, proposal_types t
      where m.designation_id = t.id
        and t.id in (select id from proposal_types where class_id = 2)
      -- group by course
      order by course
) to '/Users/vickery/CUNY_Enrollments/plas.csv' csv header

-- \d course_designation_mappings
--         Table "public.course_designation_mappings"
--      Column     |  Type   | Collation | Nullable | Default
-- ----------------+---------+-----------+----------+---------
--  discipline     | text    |           | not null |
--  course_number  | integer |           | not null |
--  designation_id | integer |           | not null |
--  is_primary     | boolean |           |          | false
--  reason         | text    |           |          |
-- Indexes:
--     "course_designation_mappings_pkey" PRIMARY KEY, btree (discipline, course_number, designation_id)
-- Foreign-key constraints:
--     "course_designation_mappings_designation_id_fkey" FOREIGN KEY (designation_id) REFERENCES proposal_types(id)
--     "course_designation_mappings_discipline_fkey" FOREIGN KEY (discipline, course_number) REFERENCES approved_courses(discipline, course_number)
--     "course_designation_mappings_reason_fkey" FOREIGN KEY (reason) REFERENCES reason_codes(abbr)



-- select * from proposal_types;
--  id | abbr  |                 full_name                  | class_id | agency_id
-- ----+-------+--------------------------------------------+----------+-----------
--   1 | NEW-U | New Undergraduate Course                   |        1 |         1
--   2 | NEW-G | New Graduate Course                        |        1 |         2
--   3 | REV-U | Revise Undergraduate Course                |        1 |         1
--   4 | REV-G | Revise Graduate Course                     |        1 |         2
--   5 | ADMIN | Migrate Perspectives Course                |        1 |         4
--   6 | FIX   | Fix CUNYfirst catalog data                 |        1 |         8
--   7 | AP    | Appreciating and Participating in the Arts |        2 |         4
--   8 | CV    | Culture and Values                         |        2 |         4
--   9 | NS    | Natural Science                            |        2 |         4
--  10 | NS+L  | Natural Science with Laboratory            |        2 |         4
--  11 | RL    | Reading Literature                         |        2 |         4
--  12 | SS    | Analyzing Social Structures                |        2 |         4
--  13 | US    | United States                              |        2 |         4
--  14 | ET    | European Traditions                        |        2 |         4
--  15 | WC    | World Cultures                             |        2 |         4
--  16 | PI    | Pre-Industrial Society                     |        2 |         4
--  20 | LPS   | Life and Physical Sciences                 |        3 |         4
--  23 | CE    | Creative Expression                        |        3 |         4
--  24 | IS    | Individual and Society                     |        3 |         4
--  25 | SW    | Scientific World                           |        3 |         4
--  26 | LANG  | Language                                   |        4 |         4
--  27 | LIT   | Literature                                 |        4 |         4

--  \d proposal_types
--                                Table "public.proposal_types"
--    Column   |  Type   | Collation | Nullable |                  Default
--  -----------+---------+-----------+----------+--------------------------------------------
--   id        | integer |           | not null | nextval('proposal_types_id_seq'::regclass)
--   abbr      | text    |           | not null |
--   full_name | text    |           | not null |
--   class_id  | integer |           | not null |
--   agency_id | integer |           | not null |
--  Indexes:
--      "proposal_types_pkey" PRIMARY KEY, btree (id)
--      "type_class" UNIQUE CONSTRAINT, btree (abbr, class_id)
--  Foreign-key constraints:
--      "proposal_types_agent_id_fkey" FOREIGN KEY (agency_id) REFERENCES agencies(id)
--      "proposal_types_class_id_fkey" FOREIGN KEY (class_id) REFERENCES proposal_classes(id)