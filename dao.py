import json
import os

import pymongo

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, 'data', 'courses.json')

DB_NAME = 'ubcapi'
COLLECTION_NAME = 'courses'

class DAO:
    def __init__(self, db_user, db_password, db_host, db_port, db_name):
        uri = "mongodb://{0}:{1}@{2}:{3}/{4}".format(
            db_user,
            db_password,
            db_host,
            db_port,
            db_name
        )
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.courses = self.db[COLLECTION_NAME]

    def get_courses(self, course_codes):
        # Use id since it is indexed
        cursor = self.courses.find(
            { "_id": { "$in": course_codes } }
        )
        return list(cursor)

    def close(self):
        self.client.close()
 
def insert_courses_from_dict(dao: DAO):
    course_dictionary = {}
    with open(PATH_JSON_COURSES, 'r') as f:
        course_dictionary = json.load(f)

    course_objects = map( 
        lambda course: 
            { 
                "_id":course[0],
                "course_code":course[0], 
                "current_course_name":course[1].strip(' '),
                "course_name_list": [],
            }, 
        course_dictionary.items() 
    )
    dao.courses.insert_many(list(course_objects))


if __name__ == '__main__':
    dao = DAO(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT'],
        DB_NAME,
    )
    
    course_codes = ['MATH100', 'MATH101']
    print( dao.get_courses(course_codes) ) 

    dao.close()