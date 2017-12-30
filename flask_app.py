from flask import Flask, jsonify, render_template, request
from flask_sslify import SSLify
import json
import os
import re

app = Flask(__name__)
sslify = SSLify(app)

pattern_course = re.compile(r'c\d+')

VERSION = '1.2'
VERSION_KEY = 'version_key'

DIGEST_KEY = 'digest_key'

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, 'data', 'courses.json')

with open(PATH_JSON_COURSES, 'r') as f:
    course_dictionary = json.load(f)

@app.route('/course/<string:course_code>', methods=['GET'])
def get_task(course_code):
    if course_code in course_dictionary:
        return jsonify({
            'code': course_code,
            'name': course_dictionary[course_code]
        })
    else:
        return jsonify({
            'code':course_code,
            'name': ''
        })

def isCourseQueryParam(param_key: str) -> bool:
    if pattern_course.match(param_key) is not None:
        return True
    return False

@app.route('/courses', methods=['GET'])
def get_courses():
    all_args: dict = request.args.to_dict()

    response_dict = {}

    if VERSION_KEY in all_args:
        response_dict[VERSION_KEY] = VERSION
    
    # TODO: Use this to prevent many requests
    if DIGEST_KEY in all_args:
        pass

    for key, value in all_args.items():
        if (isCourseQueryParam(key) and value in course_dictionary):
            course_code = value
            response_dict[course_code] = course_dictionary[course_code]

    return jsonify(response_dict)

@app.route('/')
def index():
    return render_template('index.html', version=VERSION)

# CORS
@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://ssc.adm.ubc.ca'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

if __name__ == '__main__':
    app.run()