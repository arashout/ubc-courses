import json
import os
from typing import Dict, List, Any, Optional
import datetime

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATH_JSON_COURSES = os.path.join(CURRENT_DIRECTORY, "data", "courses-live.json")

DB_NAME = "ubcapi"

DATE_FORMAT = r"%Y%m%dT%H%M%S%f"
SCORE_THRESHOLD = 10
MAX_NAME_COUNT = 10


class CourseNameScore:
    def __init__(self, name: str) -> None:
        name = name
        score = 1

    def clean(self):
        self.name = self.name.strip()

    def __lt__(self, other):
        return self.score > other.score

    # FOR DEBUGGING
    def __str__(self):
        return "{0} : {1}".format(self.name, self.score)

    def __repr__(self):
        return "{0} : {1}".format(self.name, self.score)


class CourseAbstract(me.Document):
    code = me.StringField(primary_key=True)
    name = me.StringField(required=True)
    update_time = me.StringField(require=True)
    course_name_scores = me.ListField(me.EmbeddedDocumentField(CourseNameScore))

    def clean(self):
        self.code = self.code.strip()
        self.name = self.name.strip()

    # FOR DEBUGGING
    def __str__(self):
        return "{0} : {1} -> {2}".format(self.code, self.name, self.course_name_scores)

    def __repr__(self):
        return "{0} : {1} updated: {2} -> {3}".format(self.code, self.name, self.update_time, self.course_name_scores)
    
    def asdict(self):
        dictionary = {"code": self.code, "name": self.name, "update_time": self.update_time}
        dictionary['alt_course_names'] = []
        for cns in self.course_name_scores:
            dictionary['alt_course_names'].append({'score': cns.score, 'name': cns.name})
        return dictionary

    meta: Dict[str, Any] = {"allow_inheritance": True, "abstract": True}


class Course(CourseAbstract):
    meta = {"collection": "courses-live"}


class CourseDev(CourseAbstract):
    meta = {"collection": "courses-dev"}


class CourseTest(CourseAbstract):
    meta = {"collection": "courses-test"}


class LogAbstract(me.Document):
    datestamp = me.StringField(required=True)
    path = me.StringField(required=True)
    hash_digest = me.StringField()
    data = me.DictField()
    env = me.StringField()

    meta: Dict[str, Any] = {"allow_inheritance": True, "abstract": True}


class Log(LogAbstract):
    meta = {"collection": "logs-live"}


class LogDev(LogAbstract):
    meta = {"collection": "log-dev"}


class LogTest(LogAbstract):
    meta = {"collection": "logs-test"}


class DAOWrapper:
    def __init__(
        self,
        db_user,
        db_password,
        db_host,
        db_port,
        env,
        generic_course=Course,
        generic_log=Log,
    ):
        port_number = int(db_port)
        # NOTE: 'connect=False' is to avoid connection pooling sine PyMongo is not fork-safe
        me.connect(DB_NAME, host=db_host, port=port_number, username=db_user, password=db_password, connect=False, maxPoolSize=1)
        self.generic_course = generic_course
        self.generic_log = generic_log
        self.env = env

    def insert_courses(self, courses: List[CourseAbstract]):
        try:
            self.generic_course.objects.insert(courses)
        except me.NotUniqueError:
            pass

    def upsert_course(self, _code: str, _name: str) -> CourseAbstract:
        # Make sure we have no trailing spaces
        _code = _code.strip()
        now = datetime.datetime.now()

        course: Optional[CourseAbstract] = self.get_course(_code)
        # If the course does not exist in the DB at all
        if course is None:
            course = self.generic_course(
                code=_code, name=_name, update_time=now.strftime(DATE_FORMAT)
            )
        else:
            course.update_time = now.strftime(DATE_FORMAT)
            # If the current course name is not the same as the updated one
            if course.name != _name:
                current_course_names = list(
                    map(lambda cs: cs.name, course.course_name_scores)
                )

                # If the updated course name is in the list of suggestions already
                if _name in current_course_names:
                    i = current_course_names.index(_name)
                    cns: CourseNameScore = course.course_name_scores[i]
                    cns.score = cns.score + 1

                    # The new course name has earned enough to become the default course name for this course
                    if cns.score > SCORE_THRESHOLD:
                        course.name = cns.name
                        course.course_name_scores.pop(i)

                    course.course_name_scores.sort()
                else:
                    # Pop off the least popular course name
                    # NOTE: Suggested course names are sorted in order of descending popularity
                    if len(course.course_name_scores) > MAX_NAME_COUNT - 1:
                        course.course_name_scores.pop()

                    course.course_name_scores.append(CourseNameScore(name=_name))

        course.save()
        return course

    def get_course(self, course_code: str) -> Optional[Course]:
        try:
            return self.generic_course.objects.get(pk=course_code)
        except me.DoesNotExist:
            return None

    def get_courses(self, course_codes: List[str]) -> List[CourseAbstract]:
        return list(self.generic_course.objects(pk__in=course_codes))

    def get_last_updated(self, n: int) -> List[CourseAbstract]:
        return self.generic_course.objects().order_by("-update_time")[:n]

    def insert_log(
        self, _path: str, _data=None, hash_digest=None
    ) -> Optional[LogAbstract]:
        try:
            log = self.generic_log()
            now = datetime.datetime.now()
            log.datestamp = now.strftime(DATE_FORMAT)
            log.path = _path
            log.hash_digest = hash_digest
            log.data = _data
            log.env = self.env

            return log.save()

        except me.NotUniqueError:
            return None

    def drop_collection(self, collection: me.Document):
        collection.drop_collection()

    def insert_courses_from_dict(self, course_dict: dict):
        def tuple_to_doc(course_tuple):
            now = datetime.datetime.now().strftime(DATE_FORMAT)
            return self.generic_course(
                code=course_tuple[0], 
                name=course_tuple[1],
                update_time=now
            )


        courses = list(map(tuple_to_doc, course_dict.items()))
        self.insert_courses(courses)

    def insert_courses_from_json(self, file_path: str):
        course_dictionary: dict = {}
        with open(file_path, "r") as f:
            course_dictionary = json.load(f)

        self.insert_courses_from_dict(course_dictionary)


if __name__ == "__main__":
    dao_wrapper = DAOWrapper(
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_HOST"],
        os.environ["DB_PORT"],
        os.environ.get("ENV", "manual"),
        Course,
        Log,
    )
    dao_wrapper.insert_courses_from_json(PATH_JSON_COURSES)
