from flask import Flask, jsonify, render_template, request
from flask_sslify import SSLify
import json
import os

app = Flask(__name__)
sslify = SSLify(app)

current_directory = os.path.dirname(__file__)
json_courses_path = os.path.join(current_directory, 'data', 'courses.json')

with open(json_courses_path, 'r') as f:
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

@app.route('/courses', methods=['GET'])
def get_courses():
    all_args = request.args.to_dict()

    response_dict = {}

    for _, course_code in all_args.items():
        if course_code in course_dictionary:
            response_dict[course_code] = course_dictionary[course_code]

    return jsonify(response_dict)

@app.route('/')
def index():
    return render_template('index.html')

@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://ssc.adm.ubc.ca'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    return response

if __name__ == '__main__':
    app.run()