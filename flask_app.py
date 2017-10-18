from flask import Flask, jsonify, abort, render_template
from flask_sslify import SSLify
from flask_cors import CORS, cross_origin
import json
import os

app = Flask(__name__)
SSLIFY = SSLify(app)
CORS(app)

CURRENT_DIRECTORY = os.path.dirname(__file__)

@app.route('/course/api/v1.0/code/<string:course_code>', methods=['GET'])
def get_task(course_code):
    pass


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
