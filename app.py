import os
import re
import typing
import io
from typing import Dict

from flask import Flask, jsonify, render_template, request

import models
import boto3
import json

app = Flask(__name__)

PATTERN_GET_COURSE_CODE = re.compile(r"c\d+")
# S3 Details
BUCKET_NAME = 'ubc-courses'

# Initialization steps
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(SECRET_KEY=os.urandom(16)) # Security that I was going to use for EC2
dao_wrapper = models.DAOWrapper()

s3_client = boto3.client('s3')

def dict_from_s3(client, bucket_name: str, key: str) -> Dict:
    bytes_buffer = io.BytesIO()
    client.download_fileobj(Bucket=bucket_name, Key=key, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    data = json.loads(byte_value.decode())
    return data
def dict_to_s3(client, bucket_name: str, key: str, data: Dict):
    client.put_object(Body=str.encode(json.dumps(data)), Bucket=bucket_name, Key=key)

if os.environ.get("DEV") is not None:
    with open(os.path.join('data', 'db.json')) as f:
        data = json.load(f)
        dao_wrapper.data_from_dict(data)
    print("DEV environment variable detected! Running in development mode")
else:
    data = dict_from_s3(s3_client, BUCKET_NAME, 'db.json')

    dao_wrapper.data_from_dict(data)

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

    return jsonify(response_dict)

# This should be a post request, but I'm not sure if it's allowed due to security on UBCs site 
@app.route("/courses/suggest", methods=["GET"])
def suggestCourses():
    all_args: dict = request.args.to_dict()
    course_codes = list(all_args.keys())
    response_dict = {}
    for code in course_codes:
        suggested_name = all_args.get(code, None)
        if suggested_name is not None:
            course = dao_wrapper.suggest_course(code, suggested_name)
            response_dict[code] = str(course)
        else:
            response_dict[code] = None
    # TODO: This should be an async task but I'm too lazy!
    # Also the bookmarklet takes no action with the response here anyway
    dict_to_s3(s3_client, BUCKET_NAME, 'db-new.json', dao_wrapper.state())
    return jsonify(response_dict)

@app.route("/")
def index():
    return render_template("index.html")

@app.after_request
def apply_caching(response):
    """Response headers added for CORS protection"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response