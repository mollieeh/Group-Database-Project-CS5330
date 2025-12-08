-- Sample seed data for the program evaluation schema.
-- Run after tables are created (init.sql).

INSERT INTO DEGREE (degree_id, name, level) VALUES
  (1, 'Computer Science', 'BS'),
  (2, 'Data Science', 'MS'),
  (3, 'Cybersecurity', 'Cert');

INSERT INTO COURSE (course_id, course_number, name) VALUES
  (1, 'CSCI1010', 'Introduction to Programming'),
  (2, 'CSCI2300', 'Database Systems'),
  (3, 'CSCI3400', 'Algorithms'),
  (4, 'CSCI4550', 'Network Security');

INSERT INTO INSTRUCTOR (instructor_id, name) VALUES
  ('90010001', 'Ada Lovelace'),
  ('90010002', 'Alan Turing'),
  ('90010003', 'Grace Hopper');

INSERT INTO SEMESTER (year, term) VALUES
  (2024, 'Spring'),
  (2024, 'Fall'),
  (2025, 'Spring');

INSERT INTO OBJECTIVE (objective_id, code, title, description) VALUES
  (1, 'LO1', 'Programming Fundamentals', 'Students demonstrate fluency in core programming constructs.'),
  (2, 'LO2', 'Data Management', 'Students design and query relational databases effectively.'),
  (3, 'LO3', 'Security Principles', 'Students apply defensive security practices to systems and networks.'),
  (4, 'LO4', 'Applied Machine Learning', 'Students build and evaluate predictive models.');

-- Degree-course mappings (is_core: 1 = core course for the degree).
INSERT INTO DEGREE_COURSE (degree_id, course_id, is_core) VALUES
  (1, 1, 1),
  (1, 2, 1),
  (1, 3, 1),
  (2, 2, 1),
  (2, 4, 0),
  (3, 4, 1);

-- Degree-objective mappings.
INSERT INTO DEGREE_OBJECTIVE (degree_id, objective_id) VALUES
  (1, 1),
  (1, 2),
  (1, 3),
  (2, 2),
  (2, 4),
  (3, 3);

-- Course-objective mappings scoped to degree + course pairings.
INSERT INTO COURSE_OBJECTIVE (degree_id, course_id, objective_id) VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 1),
  (1, 2, 3),
  (2, 2, 2),
  (2, 2, 4),
  (2, 4, 4),
  (3, 4, 3);

-- Sections offered.
INSERT INTO SECTION (section_id, course_id, year, term, instructor_id, section_number, enrollment_count) VALUES
  (1, 1, 2024, 'Spring', '90010001', 1, 32),
  (2, 2, 2024, 'Fall',   '90010002', 1, 28),
  (3, 4, 2024, 'Fall',   '90010003', 1, 22),
  (4, 2, 2025, 'Spring', '90010002', 2, 30);

-- Sample evaluations.
INSERT INTO EVALUATION (section_id, degree_id, objective_id, eval_method, count_A, count_B, count_C, count_F, improvement_text) VALUES
  (1, 1, 1, 'Project', 15, 10, 5, 2, 'Add weekly lab checkpoints.'),
  (2, 1, 2, 'Mid-term', 12, 9, 4, 3, 'More practice on normalization.'),
  (2, 2, 2, 'Project', 16, 8, 3, 1, 'Keep the current pacing.'),
  (3, 3, 3, 'Report', 10, 7, 3, 2, 'Introduce earlier security lab.'),
  (4, 2, 4, 'Quiz', 14, 11, 3, 2, NULL);
