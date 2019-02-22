import os
import re
import typing

from flask import Flask, jsonify, render_template, request

import models

app = Flask(__name__)

if os.environ.get("DEV") is not None:
    dao_wrapper = models.DAOWrapper(
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_HOST"],
        os.environ["DB_PORT"],
        models.CourseDev,
        models.LogDev,
    )
    print("DEV environment variable detected! Running in development mode")
else:
    dao_wrapper = models.DAOWrapper(
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_HOST"],
        os.environ["DB_PORT"],
    )

PATTERN_GET_COURSE_CODE = re.compile(r"c\d+")

API_URL = "https://ubc-api.herokuapp.com"
DIGEST_KEY = "digest_key"


def getCourseParams(args: typing.Dict[str, str]) -> typing.Dict[str, str]:
    courseParams = {}
    for key, value in args.items():
        if PATTERN_GET_COURSE_CODE.match(key) is not None:
            courseParams[key] = value

    return courseParams


@app.route("/courses", methods=["GET"])
def get_courses():
    all_args: dict = request.args.to_dict()

    response_dict = {}

    course_codes = list(getCourseParams(all_args).values())
    courses = dao_wrapper.get_courses(course_codes)

    for course in courses:
        response_dict[course.code] = course.name

    dao_wrapper.insert_log(request.path, response_dict.copy(), all_args.get(DIGEST_KEY, None))

    return jsonify(response_dict)

# This should really be a POST request but I don't think I'm allowed to send those because of CORS
@app.route("/courses/suggest", methods=["GET"])
def suggestCourses():
    all_args: dict = request.args.to_dict()
    course_codes = list(all_args.keys())
    response_dict = {}
    for code in course_codes:
        suggested_name = all_args.get(code, None)
        if suggested_name is not None:
            course = dao_wrapper.upsert_course(code, suggested_name)
            # TODO: Maybe change this response
            response_dict[code] = str(course)
        else:
            response_dict[code] = None
    
    dao_wrapper.insert_log(request.path, response_dict.copy(), all_args.get(DIGEST_KEY, None))
   
    return jsonify(response_dict)

@app.route("/")
def index():
    return render_template("index.html", api_url=API_URL)


@app.after_request
def apply_caching(response):
    """Response headers added for CORS protection"""
    response.headers["Access-Control-Allow-Origin"] = "https://ssc.adm.ubc.ca"
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == "__main__":
    app.run()
