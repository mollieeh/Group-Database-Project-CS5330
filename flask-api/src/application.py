from flask import Flask, jsonify, request, flash
import mysql.connector
import repository

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def hello_world():
    return {"items": [1,2,3,4,5]}

# DEGREE ENDPOINTS
@app.route("/degrees", methods=['GET', 'POST'])
def get_degrees():
    if request.method == 'GET':
        degrees = repository.get_degrees()
        return jsonify(degrees)

    # if post
    data = request.get_json(silent=True) or {}
    degree_name = (data.get('name') or "").strip()
    degree_level = (data.get('level') or "").strip()

    if not degree_name or not degree_level:
        return jsonify({"error": "Both name and level are required"}), 400

    try:
        created = repository.create_degree(degree_name, degree_level)
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Degree already exists"}), 409

    return jsonify(created), 201

    # getting degree by id
@app.route("/degrees/<int:degree_id>", methods=['GET'])
def degree_detail(degree_id: int):
    if request.method == 'GET':
        row = repository.get_degree_by_id(degree_id)
        if not row:
            return jsonify({"error": "Degree not found"}), 404
        return jsonify(row)
    

    #list all sections for courses in a degree
# refers to get_section_for_degree in repository.py


        #list objectives for degree given
@app.route("/degrees/<int:degree_id>/objectives", methods=['GET'])
def degree_objectives(degree_id: int):
    objectives = repository.get_objectives_for_degree(degree_id)
    return jsonify(objectives)


# COURSE ENDPOINTS
@app.route("/courses/<coursename>")
def get_course(coursename):
    return repository.get_course(coursename)

@app.route("/courses", methods=['GET', 'POST'])
def courses():
    if request.method == 'GET':
        courses = repository.get_courses()
        return jsonify(courses)

    data = request.get_json(silent=True) or {}
    course_number = (data.get('course_number') or data.get('number') or "").strip()
    course_name = (data.get('name') or "").strip()

    if not course_number or not course_name:
        return jsonify({"error": "Both course_number and name are required"}), 400

    try:
        created = repository.create_course(course_number, course_name)
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Course already exists"}), 409

    return jsonify(created), 201

@app.route("/courses/<int:course_id>", methods=['GET'])
def course_detail(course_id: int):
    if request.method == 'GET':
        row = repository.get_course_by_id(course_id)
        if not row:
            return jsonify({"error": "Course not found"}), 404
        return jsonify(row)

# INSTRUCTOR ENDPOINTS
@app.route("/instructors", methods=['GET', 'POST'])
def instructors():
    # if request.method == 'POST':
    #     data = request.get_json(silent=True) or {}
    #     instructor_id = data.get('instructor_id')
    #     instructor_name = data.get('name')
    #     if len(instructor_id) != 8 or not str(instructor_id).isnumeric():
    #         return jsonify({"error": "invalid instructor id (must be an 8 digit number)"})
        
    #     created = repository.create_instructor(instructor_id, instructor_name)
    #     return jsonify(created), 201
    
    if request.method == 'GET':
        rows = repository.get_instructors()
        return jsonify(rows)

    data = request.get_json(silent=True) or {}
    instructor_id = str(data.get('instructor_id') or "").strip()
    name = (data.get('name') or "").strip()

    if not instructor_id or not name:
        return jsonify({"error": "Both instructor_id and name are required"}), 400

    if len(instructor_id) != 8 or not instructor_id.isnumeric():
        return jsonify({"error": "invalid instructor id (must be an 8 digit number)"}), 400

    try:
        created = repository.create_instructor(instructor_id, name)
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Instructor already exists"}), 409

    return jsonify(created), 201
    
@app.route("/instructors/<instructor_id>", methods=['GET'])
def instructor_detail(instructor_id: str):
    if request.method == 'GET':
        row = repository.get_instructor_by_id(instructor_id)
        if not row:
            return jsonify({"error": "Instructor not found"}), 404
        return jsonify(row)
    
# OBJECTIVE ENDPOINTS
@app.route("/objectives", methods=['GET', 'POST'])
def objectives():
    if request.method == 'GET':
        rows = repository.get_objectives()
        return jsonify(rows)

    data = request.get_json(silent=True) or {}
    code = data.get('code')
    title = data.get('title')
    description = data.get('description')

    if not code or not title:
        return jsonify({"error": "code and title are required"}), 400

    if len(title) > 120:
        return jsonify({"error": "title must be 120 characters or less"}), 400

    try:
        created = repository.create_objective(code, title, description)
    except mysql.connector.IntegrityError:
        # Determine which unique constraint failed
        if repository.get_objective_by_code(code):
            return jsonify({"error": "Objective code must be unique"}), 409
        if repository.get_objective_by_title(title):
            return jsonify({"error": "Objective title must be unique"}), 409
        return jsonify({"error": "Objective must have unique code and title"}), 409
    except Exception:
        return jsonify({"error": "Objective could not be created"}), 500

    return jsonify(created), 201

@app.route("/objectives/<int:objective_id>", methods=['GET'])
def objective_detail(objective_id: int):
    if request.method == 'GET':
        row = repository.get_objective_by_id(objective_id)
        if not row:
            return jsonify({"error": "Objective not found"}), 404
        return jsonify(row)

# SECTION ENDPOINTS
@app.route("/sections", methods=['GET', 'POST'])
def sections():
    if request.method == 'GET':
        semester = request.args.get('semester')
        year = request.args.get('year', type=int)

        if semester and year:
            rows = repository.get_sections_by_semester(semester, year)
        else:
            rows = repository.get_sections()
        return jsonify(rows)

    data = request.get_json(silent=True) or {}
    try:
        course_id = int(data.get('course_id'))
    except (TypeError, ValueError):
        return jsonify({"error": "course_id is required"}), 400

    section_number = str(data.get('section_number') or "") # .strip()
    semester = (data.get('semester') or data.get('term') or "").strip()

    try:
        year = int(data.get('year'))
    except (TypeError, ValueError):
        return jsonify({"error": "year is required"}), 400

    # if not section_number or not semester:
    #     return jsonify({"error": "section_number and semester are required"}), 400

    # if len(section_number) > 3:
    #     return jsonify({"error": "section_number must be 3 digits or less"}), 400

    enrollment = data.get('enrollment')
    if enrollment is None:
        enrollment = data.get('enrollment_count', 0)
    instructor_id = data.get('instructor_id')

    try:
        enrollment = int(enrollment)
    except (TypeError, ValueError):
        enrollment = 0

    created = repository.create_section(
        course_id, section_number, semester, year, enrollment, instructor_id
    )
    return jsonify(created), 201

@app.route("/sections/<int:section_id>", methods=['GET'])
def section_detail(section_id: int):
    if request.method == 'GET':
        row = repository.get_section_by_id(section_id)
        if not row:
            return jsonify({"error": "Section not found"}), 404
        return jsonify(row)
    
        # list all sections for a course for a range of semesters
@app.route("/courses/<int:course_id>/sections", methods=['GET'])
def course_sections(course_id: int):
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)

    sections = repository.get_section_by_course(
        course_id, start_year, end_year
    )
    return jsonify(sections)

        # list all sections taught by an instructor for range of semesters
@app.route("/instructors/<instructor_id>/sections", methods=['GET'])
def instructor_sections(instructor_id: str):
    year = request.args.get('year', type=int)
    term = request.args.get('term')
    degree_id = request.args.get('degree_id', type=int)

    if year is None or not term:
        return jsonify({"error": "year and term are required"}), 400

    sections = repository.get_section_by_instructor(
        instructor_id, year, term, degree_id
    )
    return jsonify(sections)


# EVALUATION ENDPOINT
@app.route("/evaluations", methods=['GET', 'POST'])
def evaluations():
    if request.method == 'GET':
        rows = repository.get_evaluations()
        return jsonify(rows)

    data = request.get_json(silent=True) or {}
    try:
        section_id = int(data.get('section_id'))
        objective_id = int(data.get('objective_id'))
        degree_id = int(data.get('degree_id'))
    except (TypeError, ValueError):
        return jsonify({"error": "section_id, objective_id, and degree_id are required integers"}), 400

    eval_method = data.get('eval_method')
    
    try:
        count_A = int(data.get('count_A', 0))
        count_B = int(data.get('count_B', 0))
        count_C = int(data.get('count_C', 0))
        count_F = int(data.get('count_F', 0))
    except (TypeError, ValueError):
        return jsonify({"error": "count values must be integers"}), 400

    improvement_text = data.get('improvement_text')

    try:
        created = repository.create_evaluation(
            section_id, degree_id, objective_id, eval_method,
            count_A, count_B, count_C, count_F, improvement_text
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except mysql.connector.IntegrityError as ie:
        return jsonify({"error": str(ie)}), 409

    return jsonify(created), 201


# DEGREE COURSE QUERY ENDPOINT
        #list courses for a degree
@app.route("/degrees/<int:degree_id>/courses", methods=['GET', 'POST'])
def degree_courses(degree_id: int):
    if request.method == 'GET':
        courses = repository.get_courses_associated_with_degree(degree_id)
        return jsonify(courses)

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            course_id = int(data.get('course_id'))
        except (TypeError, ValueError):
            return jsonify({"error": "course_id is required"}), 400

        is_core = 1 if str(data.get('is_core')) in ("1", "true", "True") else 0
        result = repository.link_course_to_degree(degree_id, course_id, is_core)
        return jsonify(result), 201


# COURSE/OBJECTIVE ASSOCIATION ENDPOINT
@app.route("/course-objectives", methods=['POST'])
def course_objectives():
    data = request.get_json(silent=True) or {}
    try:
        degree_id = int(data.get('degree_id'))
        course_id = int(data.get('course_id'))
        objective_id = int(data.get('objective_id'))
    except (TypeError, ValueError):
        return jsonify({"error": "degree_id, course_id, and objective_id are required integers"}), 400

    is_core = 1 if str(data.get('is_core')) in ("1", "true", "True") else 0

    dc_link = repository.link_course_to_degree(degree_id, course_id, is_core)
    co_link = repository.link_course_objective(degree_id, course_id, objective_id)

    return jsonify({"degree_course": dc_link, "course_objective": co_link}), 201


# # INSTRUCTOR SECTIONS QUERY ENDPOINT
# @app.get("/instructors/<instructor_id>/sections")
# def api_get_sections_by_instructor(instructor_id):
#     # Optional query parameters for semester range
#     start_year = request.args.get("start_year", type=int)
#     end_year = request.args.get("end_year", type=int)

#     try:
#         rows = repository.get_section_by_instructor(instructor_id, start_year, end_year)
#         return jsonify(rows)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
# COURSE SECTIONS QUERY ENDPOINT
@app.get("/courses/<int:course_id>/sections")
def api_get_sections_by_course(course_id):
    # Optional query parameters for semester range
    start_year = request.args.get("start_year", type=int)
    end_year = request.args.get("end_year", type=int)

    try:
        rows = repository.get_section_by_course(course_id, start_year, end_year)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# DEGREE OBJECTIVES QUERY ENDPOINT
@app.get("/degrees/<int:degree_id>/objectives")
def api_get_objectives_for_degree(degree_id):
    try:
        rows = repository.get_objectives_for_degree(degree_id)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#DEGREE SECTION QUERY ENDPOINT
@app.get("/degree/<int:degree_id>/sections")
def api_get_sections_for_degree(degree_id):
    # Get query parameters
    start_year = request.args.get("start_year", type=int)
    start_term = request.args.get("start_term", type=str)
    end_year = request.args.get("end_year", type=int)
    end_term = request.args.get("end_term", type=str)

    # Validate required params
    missing = []
    if start_year is None: missing.append("start_year")
    if start_term is None: missing.append("start_term")
    if end_year is None: missing.append("end_year")
    if end_term is None: missing.append("end_term")

    if missing:
        return jsonify({"error": f"Missing parameters: {', '.join(missing)}"}), 400

    try:
        rows = repository.get_section_for_degree(
            degree_id, start_year, start_term, end_year, end_term
        )
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#COURSE OBJECTIVE ASSOSIATION QUERY
@app.get("/degree/<int:degree_id>/objectives/courses")
def api_get_courses_for_objectives(degree_id):
    try:
        rows = repository.get_courses_for_objective(degree_id)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SECTIONS BY SEMESTER ENDPOINT
@app.get("/sections/<term>/<int:year>")
def api_get_sections_by_semester(term, year):
    try:
        rows = repository.get_sections_by_semester(term, year)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(threaded=False, processes=1, debug=True)

# SECTION SUCCESS RATE QUERY
@app.get("/sections/<term>/<int:year>/success")
def api_get_sections_success_rate(term, year):
    percentage = request.args.get("percentage", type=float)
    if percentage is None:
        return jsonify({"error": "Missing query parameter: percentage"}), 400

    try:
        rows = repository.get_sections_fulfill_success_rate(term, year, percentage)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(threaded=False, processes=1, debug=True)

