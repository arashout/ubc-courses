import sqlite3
import constants
from typing import List, Tuple


class DatabaseWrapper(object):
    def __init__(self):
        self.db = sqlite3.connect(constants.DB_PATH)
        self.cursor = self.db.cursor()
        self._create_table()

    def insert_course(self, course_tuple: tuple, shouldCommit: bool):
        course_tuple = self._prepare_course_tuple(course_tuple)
        self.cursor.execute(
            '''
            INSERT INTO courses(code,name)
            VALUES(?,?)
            ''', (course_tuple[0], course_tuple[1])
        )

        if shouldCommit:
            self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()

    def save_courses(self, courses_tuple_list: List[tuple]):
        for course_tuple in courses_tuple_list:
            self.insert_course(course_tuple, False)
        self.db.commit()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses(code TEXT PRIMARY KEY, name TEXT)
        ''')
        self.db.commit()
    
    def _prepare_course_tuple(self, course_tuple: Tuple[str,str]) -> tuple:
        return ( course_tuple[0].replace(' ', '-'), course_tuple[1] )
