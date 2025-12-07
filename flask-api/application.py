from flask import Flask
import repository

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def hello_world():
    return {"items": [1,2,3,4,5]}

@app.route("/degrees")
def get_degrees():
    return repository.get_degrees()

@app.route("/courses/<coursename>")
def get_course(coursename):
    return repository.get_course(coursename)