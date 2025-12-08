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