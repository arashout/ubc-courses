import json
import os
from typing import List, NamedTuple, Optional
import datetime

from tinydb import TinyDB, Query
from tinydb.table import Document


CURRENT_DIRECTORY = os.path.dirname(__file__)
DEV_DB_URI = os.path.join(CURRENT_DIRECTORY, "data", "dev-db.json")
PROD_DB_URI = os.path.join(CURRENT_DIRECTORY, "data", "db.json")

DATE_FORMAT = r"%Y%m%dT%H%M%S%f"
SCORE_THRESHOLD = 10
MAX_NAME_COUNT = 10

class NameScore(NamedTuple):
    name: str
    score: int

class Course:
    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name
        self.updated_time = datetime.datetime.now().strftime(DATE_FORMAT)
        self.name_scores: List[NameScore] = []

    def clean(self):
        self.code = self.code.strip()
        self.name = self.name.strip()

    def to_doc(self) -> Document: 
        id = int("".join([str(ord(l)) for l in self.code]))
        return Document({
            "code": self.code,
            "name": self.name,
            "name_scores": [{"name": ns.name, "score": ns.score} for ns in self.name_scores],
            "updated_time": self.updated_time
        }, doc_id=id)

    # FOR DEBUGGING
    def __str__(self):
        return "{0} : {1} -> {2}".format(self.code, self.name, self.name_scores)

    def __repr__(self):
        return "{0} : {1} updated: {2} -> {3}".format(self.code, self.name, self.updated_time, self.name_scores)
    

def course_from_doc(doc: Document) -> Course:
    c = Course(doc['code'], doc['name'])
    c.updated_time = doc['updated_time']
    c.name_scores = [NameScore(ns['name'], ns['score']) for ns in doc['name_scores']]
    return c

class InsertResult:
    INSERTED = 1
    ALREADY_SAVED = 2

class DAOWrapper:
    def __init__(self, db_uri: str):
        self.db = TinyDB(db_uri)
        self.courses = self.db.table("courses")
        

    def insert_course(self, course: Course) -> InsertResult:
        if self.courses.contains(cond=Query().code == course.code):
            return InsertResult.ALREADY_SAVED
        self.courses.insert(course.to_doc())
        return InsertResult.INSERTED

    def insert_courses(self, courses: List[Course]):
        # TODO: Probably slow, but not sure how to ensure no collisions?
        # Need to figure out if I can set a custom ID
        # Probably need to just use SQLite haha
        for c in courses:
            self.insert_course(c)

    def suggest_course(self, _code: str, _name: str) -> Course:
        # Make sure we have no trailing spaces
        _code = _code.strip()

        course = self.get_course(_code)
        # If the course does not exist in the DB at all
        if course is None:
            course = Course(code=_code, name=_name)
            self.insert_course(course)
        else:
            # If the current course name is not the same as the updated one
            if course.name != _name:
                current_course_names = [cs.name for cs in course.name_scores]

                # If the updated course name is in the list of suggestions already
                if _name in current_course_names:
                    i = current_course_names.index(_name)
                    # Increment the counter
                    cns = course.name_scores[i]
                    cns = cns._replace(score = cns.score + 1)
                    course.name_scores[i] = cns

                    # The new course name has earned enough to become the default course name for this course
                    if cns.score > SCORE_THRESHOLD:
                        course.name = cns.name
                        course.name_scores.pop(i)

                    course.name_scores.sort()
                else:
                    # Pop off the least popular course name
                    # NOTE: Suggested course names are sorted in order of descending popularity
                    if len(course.name_scores) > MAX_NAME_COUNT - 1:
                        course.name_scores.pop()

                    course.name_scores.append(NameScore(name=_name, score=1))

        self.courses.upsert(course.to_doc(), Query().code == course.code)
        return course

    def get_course(self, course_code: str) -> Optional[Course]:
        doc = self.courses.get(Query().code == course_code)
        if doc:
            return course_from_doc(doc)
        return None

    def get_courses(self, course_codes: List[str]) -> List[Course]:
        result = self.courses.search(Query().code.one_of(course_codes))
        return [course_from_doc(c) for c in result]
    
    def drop_all(self):
        self.db.drop_tables()
    
    def close(self):
        self.db.close()

    # Utility methods
    def load_from_json(self, json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)
            courses = data['courses']
            self.insert_courses([Course(c['code'], c['name']) for c in courses])

if __name__ == "__main__":
    prod_db = DAOWrapper(PROD_DB_URI)
     
    # prod_db.load_from_json(os.path.join('data', 'courses_2020-11.json'))
    prod_db.close()