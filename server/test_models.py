import unittest
import models
import os
from typing import List


class TestDAOCourses(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(models.DEV_DB_URI)
        # Assuming insert works properly
        self.dao_wrapper.load_from_json(os.path.join("data", "test_courses.json"))

    def tearDown(self):
        self.dao_wrapper.drop_all()
        self.dao_wrapper.close()


    def test_get(self):
        code = 'MATH319'
        c: models.Course = self.dao_wrapper.get_course(code)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, "Partial Differential Equations")

        self.assertIsNone(self.dao_wrapper.get_course('RAND999'))
    
    def test_get_courses(self):
        codes = ['MATH319', 'MATH321']
        courses: List[models.Course] = self.dao_wrapper.get_courses(codes)
        self.assertEqual(len(courses),len(codes))

    def test_suggest_not_exist(self):
        code = 'MATH999'
        name = 'Test Math'
        self.assertIsNone(self.dao_wrapper.get_course(code))

        c = self.dao_wrapper.suggest_course(code, name)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, name)

    def test_suggest_exact_match(self):
        code = 'MATH320'
        name = "Real Variables I"
        c = self.dao_wrapper.get_course(code)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, name)

        c = self.dao_wrapper.suggest_course(code, name)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, name)

    def test_suggest_new_name(self):
        code = 'MATH320'
        name = 'Test1'

        c = self.dao_wrapper.suggest_course(code, name)
        self.assertIsNotNone(c)
        course_name_scores = c.name_scores
        # New suggested name
        self.assertEqual(len(course_name_scores), 1)
        self.assertEqual(course_name_scores[0].name, name)
        self.assertEqual(course_name_scores[0].score, 1)

    def test_suggest_new_name_scoring(self):
        code = 'MATH320'
        name = 'Test1'
        
        for i in range(0, models.SCORE_THRESHOLD):
            c = self.dao_wrapper.suggest_course(code, name)
            course_name_scores = c.name_scores
            # Length should not change
            self.assertEqual(len(course_name_scores), 1)
            self.assertEqual(course_name_scores[0].name, name)
            self.assertEqual(course_name_scores[0].score, i + 1)

        # Next update will make this name the default and pop it off the course
        # name list
        course = self.dao_wrapper.suggest_course(code, name)
        self.assertEqual(course.name, name)
        course_name_scores = course.name_scores
        self.assertEqual(len(course_name_scores), 0)

    def test_too_many_names(self):
        code = 'MATH320'

        name = None
        for i in range(0, models.MAX_NAME_COUNT):
            name = 'TestTitle' + str(i)
            course = self.dao_wrapper.suggest_course(code, name)
            course_name_scores = course.name_scores
            self.assertEqual(len(course_name_scores), i + 1)

        # Next name addition should pop the last name addition off since they
        # have the same popularity
        popped_name = name
        name = 'TestTitle' + str(models.MAX_NAME_COUNT)
        course = self.dao_wrapper.suggest_course(code, name)
        course_name_scores = course.name_scores
        self.assertEqual(len(course_name_scores),  models.MAX_NAME_COUNT)
        course_names = list(map(lambda cns: cns.name, course_name_scores))
        self.assertIn(name, course_names)
        self.assertNotIn(popped_name, course_names)

    def test_popularity_order(self):
        code = 'MATH320'

        for i in range(0, models.MAX_NAME_COUNT-1):
            self.add_name_n_times(code, 'Test' + str(i), i)

        c = self.dao_wrapper.get_course(code)
        self.assertEqual(c.name_scores, list(sorted(c.name_scores, key=lambda ns: ns.score)))

    def add_name_n_times(self, code:str, name:str, n: int):
        for _ in range(0,n):
            self.dao_wrapper.suggest_course(code, name)


if __name__ == '__main__':
    unittest.main()
