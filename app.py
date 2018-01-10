import os
import re
import typing

from flask import Flask, jsonify, render_template, request

import models

app = Flask(__name__)

if os.environ.get('DEV') is not None:
    dao_wrapper = models.DAOWrapper(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT'],
        models.CourseDev,
        models.LogDev
        )
else:
    dao_wrapper = models.DAOWrapper(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT']
        )
pattern_course = re.compile(r'c\d+')

API_STATUS = 'ONLINE'
API_URL = 'https://ubc-api.herokuapp.com'

VERSION = '1.3'
VERSION_KEY = 'version_key'

DIGEST_KEY = 'digest_key'


@app.route('/course/<string:course_code>', methods=['GET'])
def get_course(course_code):
    course: models.Course = dao_wrapper.get_course(course_code)

    dao_wrapper.insert_log(request.path, {course.code: course.name})

    if course is not None:
        return jsonify({
            'code': course.code,
            'name': course.name
        })
    else:
        return jsonify({
            'code': course_code,
            'name': ''
        })


@app.route('/courses', methods=['GET'])
def get_courses():
    def getCleanQueryParams(args: typing.Dict[str, str]) -> typing.Dict[str, str]:

        def isCourseQueryParam(param_key: str) -> bool:
            if pattern_course.match(param_key) is not None:
                return True
            return False

        cleanedQueryParams = {}
        for key, value in args.items():
            if isCourseQueryParam(key):
                cleanedQueryParams[key] = value

        return cleanedQueryParams

    all_args: dict = request.args.to_dict()

    response_dict = {}
    log_dict = {}

    if VERSION_KEY in all_args:
        response_dict[VERSION_KEY] = VERSION
        log_dict[VERSION_KEY] = VERSION_KEY

    # TODO: Use this to prevent many requests
    hash_digest = "NA"
    if DIGEST_KEY in all_args:
        hash_digest = all_args[DIGEST_KEY]
        log_dict[DIGEST_KEY] = hash_digest

    course_codes = list(getCleanQueryParams(all_args).values())
    courses = dao_wrapper.get_courses(course_codes)

    for course in courses:
        response_dict[course.code] = course.name

    for code in course_codes:
        log_dict[code] = response_dict.get(code, None)

    log_dict['METHOD'] = request.method

    dao_wrapper.insert_log(request.path, log_dict, hash_digest)

    return jsonify(response_dict)


@app.route('/')
def index():
    dao_wrapper.insert_log(request.path)

    return render_template('index.html', version=VERSION, api_status=API_STATUS, api_url=API_URL)


@app.after_request
def apply_caching(response):
    """Response headers added for CORS protection"""
    response.headers['Access-Control-Allow-Origin'] = 'https://ssc.adm.ubc.ca'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    app.run()
