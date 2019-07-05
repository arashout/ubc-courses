import unittest
import models
import os
from typing import List, Dict

TEST_COURSE_DICT = {
    'MATH100': 'Differential Calculus with Applications to Physical Sciences and Engineering',
    'MATH101': 'Integral Calculus with Applications to Physical Sciences and Engineering',
    'MATH152': 'Linear Systems'
}


class TestDAOCourses(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'],
            os.environ['DB_PORT'],
            "test",
            models.CourseTest,
            models.LogTest
        )
        # Assuming insert works properly
        self.dao_wrapper.insert_courses_from_dict(TEST_COURSE_DICT)

    def tearDown(self):
        self.dao_wrapper.drop_collection(models.CourseTest)
        self.dao_wrapper.drop_collection(models.LogTest)

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
        c: models.CourseAbstract = self.dao_wrapper.get_course(code)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, TEST_COURSE_DICT.get(code))

        self.assertIsNone(self.dao_wrapper.get_course('RAND999'))
    
    def test_get_courses(self):
        codes = ['MATH100', 'MATH152']
        courses: List[models.CourseAbstract] = self.dao_wrapper.get_courses(codes)
        self.assertEqual(len(courses),len(codes))

    def test_update_not_exist(self):
        code = 'MATH999'
        name = 'Test Math'
        self.assertIsNone(self.dao_wrapper.get_course(code))

        c: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, name)

    def test_update_exact_match(self):
        code = 'MATH152'

        c: models.CourseAbstract = self.dao_wrapper.upsert_course(code, TEST_COURSE_DICT[code])
        self.assertIsNotNone(c)
        self.assertEqual(c.name, TEST_COURSE_DICT[code])

    def test_update_new_name(self):
        code = 'MATH152'
        name = 'Test1'

        c: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
        self.assertIsNotNone(c)
        course_name_scores: List[models.CourseNameScore] = c.course_name_scores
        # New suggested name
        self.assertEqual(len(course_name_scores), 1)
        self.assertEqual(course_name_scores[0].name, name)
        self.assertEqual(course_name_scores[0].score, 1)

    def test_update_new_name_scoring(self):
        code = 'MATH152'
        name = 'Test1'
        
        for i in range(0, models.SCORE_THRESHOLD):
            c: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
            course_name_scores: List[models.CourseNameScore] = c.course_name_scores
            # Length should not change
            self.assertEqual(len(course_name_scores), 1)
            self.assertEqual(course_name_scores[0].name, name)
            self.assertEqual(course_name_scores[0].score, i + 1)

        # Next update will make this name the default and pop it off the course
        # name list
        course: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
        self.assertEqual(course.name, name)
        course_name_scores: List[models.CourseNameScore] = course.course_name_scores
        self.assertEqual(len(course_name_scores), 0)

    def test_too_many_names(self):
        code = 'MATH152'

        for i in range(0, models.MAX_NAME_COUNT):
            name = 'TestTitle' + str(i)
            course: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
            course_name_scores: List[models.CourseNameScore] = course.course_name_scores
            self.assertEqual(len(course_name_scores), i + 1)

        # Next name addition should pop the last name addition off since they
        # have the same popularity
        popped_name = name
        name = 'TestTitle' + str(models.MAX_NAME_COUNT)
        course: models.CourseAbstract = self.dao_wrapper.upsert_course(code, name)
        course_name_scores: List[models.CourseNameScore] = course.course_name_scores
        self.assertEqual(len(course_name_scores),  models.MAX_NAME_COUNT)
        course_names = list(map(lambda cns: cns.name, course_name_scores))
        self.assertIn(name, course_names)
        self.assertNotIn(popped_name, course_names)

    def test_popularity_order(self):
        code = 'MATH152'

        for i in range(0, models.MAX_NAME_COUNT-1):
            self.add_name_n_times(code, 'Test' + str(i), i)

        c: models.CourseAbstract = self.dao_wrapper.get_course(code)

        self.assert_is_sorted(
            list(map(lambda cns: cns.score, c.course_name_scores))
        )
    
    def test_get_last_n_updated(self):
        c1 = self.dao_wrapper.upsert_course("MATH100", "Calc I")
        c2 = self.dao_wrapper.upsert_course("MATH200", "Calc II")
        c3 = self.dao_wrapper.upsert_course("MATH300", "Calc III")
        seq_courses = self.dao_wrapper.get_last_updated(2)
        self.assertTrue(len(seq_courses) == 2)
        self.assertDictEqual(c3.asdict(), seq_courses[0].asdict())
        self.assertDictEqual(c2.asdict(), seq_courses[1].asdict())

        seq_courses = self.dao_wrapper.get_last_updated(3)
        self.assertTrue(len(seq_courses) == 3)
        self.assertDictEqual(c1.asdict(), seq_courses[2].asdict())
        

    def add_name_n_times(self, code:str, name:str, n: int):
        for _ in range(0,n):
            self.dao_wrapper.upsert_course(code, name)


class TestDAOLogs(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'],
            os.environ['DB_PORT'],
            "test",
            models.CourseTest,
            models.LogTest
        )
        # Assuming insert works properly
        self.dao_wrapper.insert_courses_from_dict(TEST_COURSE_DICT)

    def tearDown(self):
        self.dao_wrapper.drop_collection(models.CourseTest)
        self.dao_wrapper.drop_collection(models.LogTest)
    
    def test_insert(self):
        input_data =  {'MATH100': 'CALC1'}
        input_path = '/courses'
        input_hash = '1234'

        self.dao_wrapper.insert_log(input_path, input_data, input_hash)
        doc_objects = self.dao_wrapper.generic_log.objects()
        
        self.assertEqual(len(doc_objects), 1)
        doc: models.LogAbstract = doc_objects[0]
        self.assertEqual(doc.path, input_path)
        self.assertEqual(doc.hash_digest, input_hash)
        self.assertEqual(doc.data, input_data)

if __name__ == '__main__':
    unittest.main()
