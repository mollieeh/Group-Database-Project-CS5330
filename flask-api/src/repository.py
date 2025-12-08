from db_connection import create_mysql_connection

cnx = create_mysql_connection()


# DEGREES
def get_degrees():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT degree_id, name, level FROM DEGREE;")
    rows = cur.fetchall()
    cur.close()
    return rows

def create_degree(name: str, level: str):
    cur = cnx.cursor()
    cur.execute("INSERT INTO DEGREE (name, level) VALUES (%s, %s);", (name, level))
    cnx.commit()
    new_id = cur.lastrowid
    cur.close()
    return {"degree_id": new_id, "name": name, "level": level}

# COURSES
def get_course(coursename):
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT course_id, course_number, name FROM COURSE WHERE name = %s;", (coursename,))
    rows = cur.fetchall()
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
    cur.execute("INSERT INTO COURSE (course_number, name) VALUES (%s, %s);", (course_number, name))
    cnx.commit()
    new_id = cur.lastrowid
    cur.close()
    return {"course_id": new_id, "course_number": course_number, "name": name}

# INSTRUCTOR
def create_instructor(id: str, name: str):
    cur = cnx.cursor()
    cur.execute("INSERT INTO INSTRUCTOR (instructor_id, name) VALUES (%s, %s)", (id, name))
    cnx.commit()
    cur.close()
    return {"instructor_id": id, "name": name}

# OBJECTIVE
def create_objective(code: str, title: str, description: str):
    cur = cnx.cursor()
    cur.execute("INSERT INTO OBJECTIVE (code, title, description) VALUES (%s, %s, %s)", (code, title, description))
    cnx.commit()
    new_id = cur.lastrowid
    cur.close()
    return {"objective_id": new_id, "code": code, "title": title, "description": description}

def get_objectives():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT objective_id, code, title, description FROM OBJECTIVE;")
    rows = cur.fetchall()
    cur.close()
    return rows


# QUERYING SECTION
def get_courses_associated_with_degrees(degree_id: int):
    """Return courses for a degree, including whether each is core."""
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
    """Insert or update the degree-course link."""
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


def link_course_objective(degree_id: int, course_id: int, objective_id: int):
    """Link a course to an objective within a degree context."""
    cur = cnx.cursor()
    cur.execute(
        """
        INSERT INTO COURSE_OBJECTIVE (degree_id, course_id, objective_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE objective_id = VALUES(objective_id);
        """,
        (degree_id, course_id, objective_id),
    )
    cnx.commit()
    cur.close()
    return {
        "degree_id": degree_id,
        "course_id": course_id,
        "objective_id": objective_id,
    }
