import mysql.connector
from db_connection import create_mysql_connection

cnx = create_mysql_connection()


# DEGREES
def get_degrees():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT degree_id, name, level FROM DEGREE;")
    rows = cur.fetchall()
    cur.close()
    return rows

# if degree id is provideded
def get_degree_by_id(degree_id: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT degree_id, name, level FROM DEGREE WHERE degree_id = %s;", (degree_id,))
    rows = cur.fetchone()
    cur.close()
    return rows

def create_degree(name: str, level: str):
    cur = cnx.cursor()
    try:
        cur.execute("INSERT INTO DEGREE (name, level) VALUES (%s, %s);", (name, level))
        cnx.commit()
        new_id = cur.lastrowid
        return {"degree_id": new_id, "name": name, "level": level}
    except mysql.connector.IntegrityError:
        cnx.rollback()
        raise
    finally:
        cur.close()

# COURSES
def get_course(coursename):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT course_id, course_number, name FROM COURSE WHERE name = %s;", (coursename,))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_course_by_id(course_id: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT course_id, course_number, name FROM COURSE WHERE course_id = %s;", (course_id,))
    rows = cur.fetchone()
    cur.close()
    return rows

def get_courses():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT course_id, course_number, name FROM COURSE;")
    rows = cur.fetchall()
    cur.close()
    return rows

def create_course(course_number: str, name: str):
    cur = cnx.cursor()
    try:
        cur.execute("INSERT INTO COURSE (course_number, name) VALUES (%s, %s);", (course_number, name))
        cnx.commit()
        new_id = cur.lastrowid
        return {"course_id": new_id, "course_number": course_number, "name": name}
    except mysql.connector.IntegrityError:
        cnx.rollback()
        raise
    finally:
        cur.close()

# INSTRUCTOR
def create_instructor(id: str, name: str):
    cur = cnx.cursor()
    try:
        cur.execute("INSERT INTO INSTRUCTOR (instructor_id, name) VALUES (%s, %s)", (id, name))
        cnx.commit()
        return {"instructor_id": id, "name": name}
    except mysql.connector.IntegrityError:
        cnx.rollback()
        raise
    finally:
        cur.close()

def get_instructors():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT instructor_id, name FROM INSTRUCTOR;")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_instructor_by_id(instructor_id: chr):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT instructor_id, name FROM INSTRUCTOR WHERE instructor_id = %s;", (instructor_id,))
    rows = cur.fetchone()
    cur.close()
    return rows

# SECTION
def create_section(course_id: int, section_number: str, semester: str, year: int, enrollment: int, instructor_id: str):
    cur = cnx.cursor()
    # Ensure the SEMESTER record exists to satisfy FK constraint.
    cur.execute(
        "INSERT IGNORE INTO SEMESTER (year, term) VALUES (%s, %s);",
        (year, semester),
    )
    cur.execute(
        "INSERT INTO SECTION (course_id, section_number, term, year, enrollment_count, instructor_id) VALUES (%s, %s, %s, %s, %s, %s);",
        (course_id, section_number, semester, year, enrollment, instructor_id),
    )
    cnx.commit()
    new_id = cur.lastrowid
    cur.close()
    return {
        "section_id": new_id, 
        "course_id": course_id, 
        "section_number": section_number,
        "semester": semester, 
        "year": year, 
        "enrollment": enrollment, 
        "instructor_id": instructor_id
    }

def get_sections():
    cur = cnx.cursor(dictionary=True)
    cur.execute("""SELECT s.section_id, s.course_id, c.course_number, c.name AS course_name, s.section_number, s.term AS semester, s.year, s.enrollment_count AS enrollment, s.instructor_id, i.name AS instructor_name
                FROM SECTION s
                JOIN COURSE c on s.course_id = c.course_id
                JOIN INSTRUCTOR i on s.instructor_id = i.instructor_id
                ORDER BY s.year DESC, 
                 FIELD(s.term, 'Spring', 'Summer', 'Fall') DESC,
                 c.course_number, s.section_number;""")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_section_by_id(section_id: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute("""SELECT s.section_id, s.course_id, c.course_number, c.name as course_name, s.section_number, s.term AS semester, s.year, s.enrollment_count AS enrollment, s.instructor_id, i.name as instructor_name
        FROM SECTION s
        JOIN COURSE c ON s.course_id = c.course_id
        LEFT JOIN INSTRUCTOR i ON s.instructor_id = i.instructor_id
        WHERE s.section_id = %s;
    """, (section_id,))
    row = cur.fetchone()
    cur.close()
    return row

def get_section_by_instructor(instructor_id: str, year: int = None, term: str = None, degree_id: int = None):
    # get sections taught by instructor filtered by year/term and optionally degree
    cur = cnx.cursor(dictionary=True)
    conditions = ["s.instructor_id = %s"]
    params = [instructor_id]
    join_degree = ""

    if year is not None:
        conditions.append("s.year = %s")
        params.append(year)
    if term:
        conditions.append("s.term = %s")
        params.append(term)
    if degree_id is not None:
        join_degree = "JOIN DEGREE_COURSE dc ON dc.course_id = s.course_id"
        conditions.append("dc.degree_id = %s")
        params.append(degree_id)

    where_clause = " AND ".join(conditions)
    query = f"""
            SELECT 
                s.section_id,
                s.section_number,
                s.term AS term,
                s.year,
                s.enrollment_count,
                s.course_id,
                c.course_number,
                c.name AS course_name,
                s.instructor_id,
                i.name AS instructor_name
            FROM SECTION s
            JOIN COURSE c ON s.course_id = c.course_id
            JOIN INSTRUCTOR i ON s.instructor_id = i.instructor_id
            {join_degree}
            WHERE {where_clause}
            ORDER BY s.year DESC, FIELD(s.term, 'Spring', 'Summer', 'Fall') DESC, c.course_number, s.section_number;"""
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_section_by_course(course_id: int, start_year: int = None, end_year: int = None):
    # get sections given a course for specific range of semesters
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
            SELECT s.section_number, i.name AS instructor_name, c.name AS course_name, s.year, s.term AS semester 
                FROM COURSE c
                JOIN SECTION s on c.course_id = s.course_id
                JOIN INSTRUCTOR i on s.instructor_id = i.instructor_id
                WHERE c.course_id = %s
	                AND (s.year BETWEEN %s AND %s)
                ORDER BY s.year DESC, FIELD(s.term, 'Spring', 'Summer', 'Fall') DESC, s.section_number;""", (course_id, start_year, end_year))
    rows = cur.fetchall()
    cur.close()
    return rows


# OBJECTIVE
def create_objective(code: str, title: str, description: str):
    cur = cnx.cursor()
    try:
        cur.execute("INSERT INTO OBJECTIVE (code, title, description) VALUES (%s, %s, %s)", (code, title, description))
        cnx.commit()
        new_id = cur.lastrowid
        return {"objective_id": new_id, "code": code, "title": title, "description": description}
    except mysql.connector.IntegrityError:
        cnx.rollback()
        raise
    finally:
        cur.close()

def get_objectives():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT objective_id, code, title, description FROM OBJECTIVE;")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_objective_by_id(objective_id: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT objective_id, code, title, description FROM OBJECTIVE WHERE objective_id = %s;", (objective_id,))
    rows = cur.fetchone()
    cur.close()
    return rows

def get_objective_by_code(code: str):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT objective_id, code, title, description FROM OBJECTIVE WHERE code = %s;", (code,))
    rows = cur.fetchone()
    cur.close()
    return rows

def get_objective_by_title(title: str):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT objective_id, code, title, description FROM OBJECTIVE WHERE title = %s;", (title,))
    rows = cur.fetchone()
    cur.close()
    return rows


# EVALUATIONS
def create_evaluation(section_id: int, degree_id: int, objective_id: int, eval_method: str = None, count_A: int = 0, count_B: int = 0, count_C: int = 0, count_F: int = 0, improvement_text: str = None):
    cur = cnx.cursor()
    try:
        # Verify objective exists to avoid FK failures.
        cur.execute("SELECT 1 FROM OBJECTIVE WHERE objective_id = %s;", (objective_id,))
        if cur.fetchone() is None:
            raise ValueError(f"Objective {objective_id} does not exist")

        # Ensure the degree/objective combo exists for FK constraint.
        cur.execute(
            """
            INSERT INTO DEGREE_OBJECTIVE (degree_id, objective_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE objective_id = VALUES(objective_id);
            """,
            (degree_id, objective_id),
        )

        cur.execute("""
            INSERT INTO EVALUATION (section_id, degree_id, objective_id, eval_method, count_A, count_B, count_C, count_F, improvement_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                eval_method = VALUES(eval_method),
                count_A = VALUES(count_A),
                count_B = VALUES(count_B),
                count_C = VALUES(count_C),
                count_F = VALUES(count_F),
                improvement_text = VALUES(improvement_text);
            """, (section_id, degree_id, objective_id, eval_method, count_A, count_B, count_C, count_F,
                                                              improvement_text))
        cnx.commit()
    except mysql.connector.Error:
        cnx.rollback()
        cur.close()
        raise
    cur.close()
    return {
        "section_id": section_id,
        "objective_id": objective_id,
        "degree_id": degree_id,
        "eval_method": eval_method,
        "count_A": count_A,
        "count_B": count_B,
        "count_C": count_C,
        "count_F": count_F,
        "improvement_text": improvement_text
    }

# check this one!!
def get_evaluations():
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
        SELECT e.section_id, e.objective_id, e.degree_id,
               e.eval_method, e.count_A, e.count_B, e.count_C, e.count_F,
               e.improvement_text,
               s.section_number, s.term AS semester, s.year,
               c.course_number, c.name as course_name,
               o.code as objective_code, o.title as objective_title,
               d.name as degree_name, d.level as degree_level
        FROM EVALUATION e
        JOIN SECTION s ON e.section_id = s.section_id
        JOIN COURSE c ON s.course_id = c.course_id
        JOIN OBJECTIVE o ON e.objective_id = o.objective_id
        JOIN DEGREE d ON e.degree_id = d.degree_id
        ORDER BY s.year DESC, FIELD(s.term, 'Spring', 'Summer', 'Fall') DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    return rows



# QUERYING SECTION
def get_courses_associated_with_degrees(degree_id: int):
    # Return courses for a degree, including whether each is core
    cur = cnx.cursor(dictionary=True)
    cur.execute(
        """
        SELECT c.course_id,
               c.course_number,
               c.name,
               dc.is_core
        FROM DEGREE_COURSE dc
        JOIN COURSE c ON c.course_id = dc.course_id
        WHERE dc.degree_id = %s
        ORDER BY c.course_number;
        """,
        (degree_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


# DEGREE-COURSE AND COURSE-OBJECTIVE ASSOCIATIONS
def link_course_to_degree(degree_id: int, course_id: int, is_core: int = 0):
    # Insert or update the degree-course link.
    cur = cnx.cursor()
    cur.execute(
        """
        INSERT INTO DEGREE_COURSE (degree_id, course_id, is_core)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE is_core = VALUES(is_core);
        """,
        (degree_id, course_id, is_core),
    )
    cnx.commit()
    cur.close()
    return {"degree_id": degree_id, "course_id": course_id, "is_core": is_core}

def get_courses_associated_with_degree(degree_id: int):
    # get courses for a degree, denotes whether each is core
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
                SELECT d.name AS degree_name, d.level AS degree_level, c.name AS course_name, c.course_number, 
                CASE 
                    WHEN dc.is_core = 1 THEN 'Core' 
                    ELSE 'Elective' 
                END AS course_type, dc.is_core
                FROM DEGREE d
                JOIN DEGREE_COURSE dc on d.degree_id = dc.degree_id
                JOIN COURSE c on dc.course_id = c.course_id
                WHERE d.degree_id = %s
                ORDER BY c.course_number;
    """, (degree_id,))
    rows = cur.fetchall()
    cur.close()
    return rows

# Given a degree: List all sections that are being offered (in chronological order, where user can supply the time range)
def get_section_for_degree(degree_id: int, start_year: int, start_term: str, end_year: int, end_term: str):
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            s.section_id,
            s.course_id,
            c.course_number,
            c.name AS course_name,
            s.year,
            s.term,
            s.section_number,
            s.instructor_id,
            s.enrollment_count
        FROM SECTION s
        JOIN COURSE c ON c.course_id = s.course_id
        JOIN DEGREE_COURSE dc ON dc.course_id = s.course_id
        WHERE dc.degree_id = %s
          AND (
                (s.year > %s) OR
                (s.year = %s AND FIELD(s.term,'Spring','Summer','Fall') >= FIELD(%s,'Spring','Summer','Fall'))
              )
          AND (
                (s.year < %s) OR
                (s.year = %s AND FIELD(s.term,'Spring','Summer','Fall') <= FIELD(%s,'Spring','Summer','Fall'))
              )
        ORDER BY 
            s.year,
            FIELD(s.term,'Spring','Summer','Fall'),
            s.course_id,
            s.section_number;
    """, (
        degree_id, start_year, start_year, start_term,
        end_year, end_year, end_term
    ))

    rows = cur.fetchall()
    cur.close()
    return rows 



        #course obj.
def link_course_objective(degree_id: int, course_id: int, objective_id: int):
    # Link a course to an objective within a degree context
    cur = cnx.cursor()
    try:
        # Ensure the degree-objective association exists for FK constraint.
        cur.execute(
            """
            INSERT INTO DEGREE_OBJECTIVE (degree_id, objective_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE objective_id = VALUES(objective_id);
            """,
            (degree_id, objective_id),
        )
        # Link course to degree as well for completeness (no-op if already exists).
        cur.execute(
            """
            INSERT INTO DEGREE_COURSE (degree_id, course_id, is_core)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE is_core = is_core;
            """,
            (degree_id, course_id),
        )
        # Finally link course to objective within the degree context.
        cur.execute(
            """
            INSERT INTO COURSE_OBJECTIVE (degree_id, course_id, objective_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE objective_id = VALUES(objective_id);
            """,
            (degree_id, course_id, objective_id),
        )
        cnx.commit()
    except mysql.connector.Error:
        cnx.rollback()
        cur.close()
        raise
    cur.close()
    return {
        "degree_id": degree_id,
        "course_id": course_id,
        "objective_id": objective_id,
    }


def get_objectives_for_degree(degree_id: int):
    #get objectives associated w a degree
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
        SELECT d.name AS degree_name, d.level AS degree_level, o.title AS objective_title, o.code AS objective_code, o.description AS objective_description 
                FROM DEGREE d 
                JOIN DEGREE_OBJECTIVE do on d.degree_id = do.degree_id
                JOIN OBJECTIVE o on do.objective_id = o.objective_id
                WHERE d.degree_id = %s
                ORDER BY o.code;
    """, (degree_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


#Given a degree, list all courses associated with each objective 
def get_courses_for_objective(degree_id: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
            SELECT 
                o.objective_id,
                o.code AS objective_code,
                o.title AS objective_title,
                c.course_id,
                c.course_number,
                c.name AS course_name
        FROM DEGREE_OBJECTIVE d_obj
        JOIN COURSE_OBJECTIVE co 
               ON co.degree_id = d_obj.degree_id
              AND co.objective_id = d_obj.objective_id
        JOIN COURSE c 
               ON c.course_id = co.course_id
        JOIN OBJECTIVE o
               ON o.objective_id = d_obj.objective_id
        WHERE d_obj.degree_id = %s
        ORDER BY o.code, c.course_number;
                """, (degree_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


# EVALUATION QUERIES

#Given a semester: list all the sections, and for each section, determine whether the evaluation information has been entered
#(also differential whether the optional “improvement” paragraph has been entered), partially entered (some information has been entered), or not entered at all  
def get_sections_by_semester(term: str, year: int):
    cur = cnx.cursor(dictionary=True)
    cur.execute(
        """
        SELECT 
            s.section_id,
            s.course_id,
            c.course_number,
            c.name AS course_name,
            s.section_number,
            s.term,
            s.year,

            e.count_A, e.count_B, e.count_C, e.count_F,
            e.improvement_text,

            CASE
                WHEN e.section_id IS NULL THEN 'Not Entered'
                WHEN 
                    (e.count_A IS NOT NULL OR e.count_B IS NOT NULL OR 
                     e.count_C IS NOT NULL OR e.count_F IS NOT NULL
                    ) 
                    AND e.improvement_text IS NULL
                THEN 'Partially Entered'
                ELSE 'Entered'
            END AS eval_status

        FROM SECTION s
        JOIN COURSE c ON c.course_id = s.course_id
        LEFT JOIN EVALUATION e 
            ON e.section_id = s.section_id

        WHERE s.term = %s AND s.year = %s
        ORDER BY s.year, 
                 FIELD(s.term,'Spring','Summer','Fall'),
                 c.course_number, s.section_number;
        """,
        (term, year)
    )
    rows = cur.fetchall()
    cur.close()
    return rows


#Given a semester: Given a semester, ask the user for a percentage, then output the sections where the numbers of students that did not get the ‘F’ grade reach that percentage.
#(You can also incorporate the information into the previous query)
def get_sections_fulfill_success_rate(semester: str, year: int, percentage: float):
    threshold = percentage/100.0

    cur = cnx.cursor(dictionary=True)
    cur.execute(
        """
        SELECT 
            s.section_id,
            s.course_id,
            c.course_number,
            c.name AS course_name,
            s.section_number,
            s.semester,
            s.year,
            
            e.count_A,
            e.count_B,
            e.count_C,
            e.count_F,

            (e.count_A + e.count_B + e.count_C) /
            NULLIF(e.count_A + e.count_B + e.count_C + e.count_F, 0)
            AS success_rate

        FROM SECTION s
        JOIN COURSE c ON c.course_id = s.course_id
        JOIN EVALUATION e ON e.section_id = s.section_id

        WHERE s.semester = %s
          AND s.year = %s
          AND (
                (e.count_A + e.count_B + e.count_C) /
                NULLIF(e.count_A + e.count_B + e.count_C + e.count_F, 0)
              ) >= %s

        ORDER BY success_rate DESC;
        """,
        (semester, year, threshold),
    )
    rows = cur.fetchall()
    cur.close()
    return rows

