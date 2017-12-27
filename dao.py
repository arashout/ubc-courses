import json
import os

import pymongo

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, 'data', 'courses.json')

DB_NAME = 'ubcapi'
COLLECTION_NAME = 'courses'


class CourseScore:
    def __init__(self, code, name, score):
        self.code = code
        self.name = name
        self.score = score


class CourseDocument:
    def __init__(self, code, name, score=1):
        self.code = code.strip(' ')
        self.name = name.strip(' ')
        self.score = score

    def doc(self):
        return {
            "_id": self.code,
            "name": self.name,
            "course_name_list": [
                CourseScore(self.code, self.name, 1).__dict__
            ],
        }


class DAO:
    def __init__(self, db_user, db_password, db_host, db_port):
        uri = "mongodb://{0}:{1}@{2}:{3}/{4}".format(
            db_user,
            db_password,
            db_host,
            db_port,
            DB_NAME
        )
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[DB_NAME]
        self.courses = self.db[COLLECTION_NAME]

    def get_courses(self, codes):
        # Use id since it is indexed
        cursor = self.courses.find(
            {"_id": {"$in": codes}}
        )
        return list(cursor)

    def upsert_course(self, code, name, skip_vote=True):
        if skip_vote:
            self.courses.replace_one(
                {"_id": code},
                CourseDocument(code, name)
            )
        else:
            course = self.courses.find_one({"_id": code})
            if course is None:
                self.courses.insert_one(CourseDocument(code, name))

    def close(self):
        self.client.close()


def insert_courses_from_dict(dao: DAO):
    course_dictionary = {}
    with open(PATH_JSON_COURSES, 'r') as f:
        course_dictionary = json.load(f)

    def tuple_to_doc(course_tuple):
        cd = CourseDocument(course_tuple[0], course_tuple[1])
        return cd.doc()

    course_objects = map(tuple_to_doc, course_dictionary.items())
    dao.courses.insert_many(list(course_objects))


if __name__ == '__main__':
    dao = DAO(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT']
    )
    course_codes = ['MATH100', 'MATH101']
    insert_courses_from_dict(dao)

    dao.close()
