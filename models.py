import json
import os
import typing

import mongoengine as me

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, 'data', 'courses.json')

DB_NAME = 'ubcapi'

SCORE_THRESHOLD = 3
MAX_NAME_COUNT = 3


class CourseNameScore(me.EmbeddedDocument):
    name = me.StringField(required=True)
    score = me.IntField(min_value=1, default=1)

    def clean(self):
        self.name = self.name.strip()

    def __lt__(self, other):
        return self.score > other.score

    # FOR DEBUGGING
    def __str__(self):
        return "{0} : {1}".format(self.name, self.score)

    def __repr__(self):
        return "{0} : {1}".format(self.name, self.score)


class Course(me.Document):
    code = me.StringField(primary_key=True)
    name = me.StringField(required=True)
    course_name_scores = me.ListField(
        me.EmbeddedDocumentField(CourseNameScore))

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
        # NOTE: 'connect=False' is to avoid connection pooling sine PyMongo is not fork-safe
        # Basically it will make PythonAnywhere setup work...
        me.connect(host=uri, connect=False)

    def insert_many(self, courses: typing.List[Course]):
        Course.objects.insert(courses)

    def insert(self, course: Course):
        Course.objects.insert(course)

    # TODO: Way too much logic in this method. Comment and fix somehow
    def update_course(self, _code: str, _name: str):
        c = self.get(_code)
        if c is None:
            self.insert(Course(code=_code, name=_name))
        else:
            if c.name == _name:
                return
            else:
                current_course_names = list(
                    map(lambda cs: cs.name,  c.course_name_scores))

                if _name in current_course_names:
                    i = current_course_names.index(_name)
                    cns: CourseNameScore = c.course_name_scores[i]
                    cns.score = cns.score + 1

                    if cns.score > SCORE_THRESHOLD:
                        c.name = cns.name
                        c.course_name_scores.pop(i)

                    c.course_name_scores.sort()

                    c.save()
                else:
                    if len(c.course_name_scores) > MAX_NAME_COUNT:
                        c.course_name_scores.pop()

                    c.course_name_scores.append(CourseNameScore(name=_name))

                    c.save()

    def get(self, course_code: str) -> typing.Optional[Course]:
        try:
            return Course.objects.get(pk=course_code)
        except me.DoesNotExist:
            return None

    def get_many(self, course_codes: typing.List[str]) -> typing.List[Course]:
        return list(Course.objects(pk__in=course_codes))

    def drop_courses(self):
        Course.drop_collection()


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
