import os

from flask import Flask, jsonify, render_template, request
# from flask_sslify import SSLify

import models

app = Flask(__name__)
# sslify = SSLify(app)

dao_wrapper = models.DAOWrapper(
    os.environ['DB_USER'],
    os.environ['DB_PASSWORD'],
    os.environ['DB_HOST'],
    os.environ['DB_PORT']
)

VERSION = '1.2'
VERSION_KEY = 'version_key'

API_STATUS = 'OFFLINE (maintenance)'

@app.route('/course/<string:course_code>', methods=['GET'])
def get_course(course_code):
    course: models.Course = dao_wrapper.get(course_code)
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
    all_args = request.args.to_dict()

    response_dict = {}

    if VERSION_KEY in all_args:
        response_dict[VERSION_KEY] = VERSION
        # Delete the query key so we don't iterate over it below
        del all_args[VERSION_KEY]

    course_codes = list(all_args.values())
    courses = dao_wrapper.get_many(course_codes)
    for course in courses:
        response_dict[course.code] = course.name

    return jsonify(response_dict)


@app.route('/')
def index():
    return render_template('index.html', version=VERSION, status=API_STATUS)


@app.after_request
def apply_caching(response):
    """Response headers added for CORS protection"""
    response.headers['Access-Control-Allow-Origin'] = 'https://ssc.adm.ubc.ca'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    app.run()
