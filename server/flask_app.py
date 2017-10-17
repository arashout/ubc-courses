from flask import Flask, jsonify, abort, render_template
from flask_sslify import SSLify
from flask_cors import CORS, cross_origin
import json
import os

app = Flask(__name__)
SSLIFY = SSLify(app)
CORS(app)

current_directory = os.path.dirname(__file__)
json_courses_path = os.path.join(current_directory, 'courses_stable.json')

with open(json_courses_path, 'r') as f:
    course_dictionary = json.load(f)


@app.route('/course/api/v1.0/code/<string:course_code>', methods=['GET'])
def get_task(course_code):
    if course_code in course_dictionary:
        return jsonify({
            'code': course_code,
            'name': course_dictionary[course_code]
        })
    else:
        abort(404)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
