from flask import Flask, jsonify, request, flash
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

    created = repository.create_degree(degree_name, degree_level)
    return jsonify(created), 201

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

    created = repository.create_course(course_number, course_name)
    return jsonify(created), 201


# INSTRUCTOR ENDPOINTS
@app.route("/instructors", methods=['GET', 'POST'])
def instructors():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        instructor_id = data.get('instructor_id')
        instructor_name = data.get('name')
        if len(instructor_id) != 8 or not str(instructor_id).isnumeric():
            return jsonify({"error": "invalid instructor id (must be an 8 digit number)"})
        
        created = repository.create_instructor(instructor_id, instructor_name)
        return jsonify(created), 201
    
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
    created = repository.create_objective(code, title, description)
    return jsonify(created), 201

# DEGREE COURSE QUERY ENDPOINT
@app.route("/degrees/<int:degree_id>/courses", methods=['GET'])
def degree_courses(degree_id: int):
    courses = repository.get_courses_associated_with_degrees(degree_id)
    return jsonify(courses)


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
