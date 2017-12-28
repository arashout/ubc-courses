import os
import unittest

import models


class CourseTest(models.Course):
    meta = {'collection': 'course_testing'}


class DAOTest(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'],
            os.environ['DB_PORT']
        )
