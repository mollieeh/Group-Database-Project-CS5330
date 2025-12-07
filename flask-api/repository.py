from db_connection import create_mysql_connection
cnx = create_mysql_connection()


def get_degrees():
    cur = cnx.cursor()
    cur.execute("SELECT * FROM DEGREE;")
    return cur.fetchall()

def get_course(coursename):
    cur = cnx.cursor()
    cur.execute("SELECT * FROM COURSE WHERE name = %s;", (coursename,))
    return cur.fetchall()