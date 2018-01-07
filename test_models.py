import unittest
import models
import os
import typing


class CourseTest(models.AbstractCourse):
    meta = {
        'collection': 'courses-test'
    }

class LogTest(models.AbstractLog):
    meta = {
        'collection': 'logs-test'
    }

COURSE_DICT = {
    'MATH100': 'Differential Calculus with Applications to Physical Sciences and Engineering',
    'MATH101': 'Integral Calculus with Applications to Physical Sciences and Engineering',
    'MATH152': 'Linear Systems'
}


class TestDAO(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'],
            os.environ['DB_PORT'],
            CourseTest,
            LogTest
        )
        # Assuming insert works properly
        models.insert_courses_from_dict(self.dao_wrapper, COURSE_DICT)

    def tearDown(self):
        self.dao_wrapper.drop_collection(CourseTest)

    def assert_is_sorted(self, container: list, ascending=False):
        if not container or len(container) == 1:
            self.fail('Container is empty or only has one lelement')

        prev = container[0]
        for i in range(1, len(container)):
            cur = container[i]
            if(ascending):
                self.assertLessEqual(prev, cur)
            else:
                self.assertLessEqual(cur, prev)
            prev = cur

    def test_get(self):
        code = 'MATH152'
        c: models.AbstractCourse = self.dao_wrapper.get_course(code)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, COURSE_DICT.get(code))

        self.assertIsNone(self.dao_wrapper.get_course('RAND999'))

    def test_update_not_exist(self):
        code = 'MATH999'
        name = 'Test Math'
        self.assertIsNone(self.dao_wrapper.get_course(code))

        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, name)

    def test_update_exact_match(self):
        code = 'MATH152'

        c: models.AbstractCourse = self.dao_wrapper.update_course(code, COURSE_DICT[code])
        self.assertIsNotNone(c)
        self.assertEqual(c.name, COURSE_DICT[code])

    def test_update_new_name(self):
        code = 'MATH152'
        name = 'Test1'

        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        self.assertIsNotNone(c)
        course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
        # New suggested name
        self.assertEqual(len(course_name_scores), 1)
        self.assertEqual(course_name_scores[0].name, name)
        self.assertEqual(course_name_scores[0].score, 1)

    def test_update_new_name_scoring(self):
        code = 'MATH152'
        name = 'Test1'

        for i in range(0, models.SCORE_THRESHOLD):
            c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
            course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
            # Length should not change
            self.assertEqual(len(course_name_scores), 1)
            self.assertEqual(course_name_scores[0].name, name)
            self.assertEqual(course_name_scores[0].score, i + 1)

        # Next update will make this name the default and pop it off the course
        # name list
        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        self.assertEqual(c.name, name)
        course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
        self.assertEqual(len(course_name_scores), 0)

    def test_too_many_names(self):
        code = 'MATH152'

        for i in range(0, models.MAX_NAME_COUNT):
            name = 'TestTitle' + str(i)
            c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
            course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
            self.assertEqual(len(course_name_scores), i + 1)

        # Next name addition should pop the last name addition off since they
        # have the same popularity
        popped_name = name
        name = 'TestTitle' + str(i + 1)
        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
        self.assertEqual(len(course_name_scores),  models.MAX_NAME_COUNT)
        course_names = list(map(lambda cns: cns.name, course_name_scores))
        self.assertIn(name, course_names)
        self.assertNotIn(popped_name, course_names)

    def test_popularity_order(self):
        code = 'MATH152'

        def add_name_n_times(_name, n: int):
            for i in range(0,n):
                self.dao_wrapper.update_course(code, _name)

        for i in range(0, models.MAX_NAME_COUNT-1):
            add_name_n_times('Test' + str(i), i)

        c: models.AbstractCourse = self.dao_wrapper.get_course(code)
        print(c.course_name_scores)
        self.assert_is_sorted(
            list(map(lambda cns: cns.score, c.course_name_scores))
        )


if __name__ == '__main__':
    unittest.main()
