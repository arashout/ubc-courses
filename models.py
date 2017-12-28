import json
import os
import typing

import mongoengine as me

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, 'data', 'courses.json')

DB_NAME = 'ubcapi'


class CourseNameScore:
    name = me.StringField(required=True)
    score = me.IntField(min_value=1, default=1)

    def clean(self):
        self.name = self.name.strip()


class Course(me.Document):
    code = me.StringField(primary_key=True)
    name = me.StringField(required=True)
    course_name_scores = me.ListField()

    def clean(self):
        self.name = self.name.strip()

    # FOR DEBUGGING
    def __str__(self):
        return "{0} : {1} -> {2}".format(self.code, self.name, self.course_name_scores)

    def __repr__(self):
        return "{0} : {1} -> {2}".format(self.code, self.name, self.course_name_scores)


class DAOWrapper:
    def __init__(self, db_user, db_password, db_host, db_port):
        uri = "mongodb://{0}:{1}@{2}:{3}/{4}".format(
            db_user,
            db_password,
            db_host,
            db_port,
            DB_NAME
        )
        # I hate this... Why does it not give me back a connection object
        me.connect(host=uri)

    def insert_many(self, courses: typing.List[Course]):
        Course.objects.insert(courses)

    def insert(self, course: Course):
        course.save()

    def get(self, course_code: str) -> Course:
        try:
            return Course.objects.get(pk=course_code)
        except me.DoesNotExist:
            return None


def insert_courses_from_dict(dao_wrapper: DAOWrapper):
    course_dictionary = {}
    with open(PATH_JSON_COURSES, 'r') as f:
        course_dictionary = json.load(f)

    def tuple_to_doc(course_tuple):
        return Course(code=course_tuple[0], name=course_tuple[1])

    courses = list(map(tuple_to_doc, course_dictionary.items()))
    dao_wrapper.insert_many(courses)


if __name__ == '__main__':
    dao_wrapper = DAOWrapper(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT']
    )
    insert_courses_from_dict(dao_wrapper)
    print(dao_wrapper.get('MATH100'))
