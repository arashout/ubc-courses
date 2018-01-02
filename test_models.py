import unittest
import models
import os
import typing


class CourseTest(models.AbstractCourse):
    meta = {
        'collection': 'courses-test'
    }

COURSE_DICT = {
    'APSC150': ' Engineering Case Studies',
    'APSC160': 'Introduction to Computation in Engineering Design',
    'CHEM154': 'Chemistry for Engineering',
    'CIVL200': 'Engineering and Sustainable Development',
    'ENGL112': 'Strategies for University Writing',
    'EOSC114': 'The Catastrophic Earth: Natural Disasters',
    'LING101': 'Languages of the World',
    'MATH100': 'Differential Calculus with Applications to Physical Sciences and Engineering',
    'MATH101': 'Integral Calculus with Applications to Physical Sciences and Engineering',
    'MATH152': 'Linear Systems',
    'MATH253': 'Multivariable Calculus',
    'MATH255': 'Ordinary Differential Equations',
    'MATH307': 'Applied Linear Algebra',
    'MECH220': 'Technical Skills Practicum',
    'MECH221': 'Engineering Science I',
    'MECH222': 'Engineering Science II',
    'MECH223': 'Introduction to the Mechanical Design Process',
    'MECH224': 'Integration of Engineering Concepts I',
    'MECH225': 'Integration of Engineering Concepts II',
    'MECH226': 'Technical Communication for Mechanical Engineers',
    'MECH305': 'Data Analysis and Mechanical Engineering Laboratories',
    'MECH325': 'Mechanical Design I',
    'MECH326': 'Mechanical Design II',
    'MECH328': 'Mechanical Engineering Design Project',
    'MECH358': 'Engineering Analysis',
    'MECH360': 'Mechanics of Materials',
    'MECH368': 'Engineering Measurements and Instrumentation',
    'MECH375': 'Heat Transfer',
    'MECH380': 'Fluid Dynamics',
    'PHIL120': 'Introduction to Critical Thinking',
    'PHYS153': ' Elements of Physics',
    'PHYS170': 'Mechanics I'
}

class TestDAO(unittest.TestCase):
    def setUp(self):
        self.dao_wrapper = models.DAOWrapper(
            os.environ['DB_USER'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_HOST'],
            os.environ['DB_PORT'],
            CourseTest
        )
        # Assuming insert works properly
        models.insert_courses_from_dict(self.dao_wrapper, COURSE_DICT)
    
    def tearDown(self):
        self.dao_wrapper.drop_collection(CourseTest)

    def test_get(self):
        code = 'MATH101'
        c: models.AbstractCourse = self.dao_wrapper.get(code)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, COURSE_DICT.get(code))

        self.assertIsNone(self.dao_wrapper.get('RAND999'))

    def test_update_not_exist(self):
        code = 'MATH999'
        name = 'Test Math'
        self.assertIsNone(self.dao_wrapper.get(code))

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
        self.assertEqual( len(course_name_scores), 1)
        self.assertEqual(course_name_scores[0].name, name)
        self.assertEqual(course_name_scores[0].score, 1)
    
    def test_update_new_name_scoring(self):
        code = 'MATH152'
        name = 'Test1'

        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores

        for i in range(1, models.MAX_NAME_COUNT):
            c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
            course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
            self.assertEqual( len(course_name_scores), 1) # Length should not change
            self.assertEqual(course_name_scores[0].name, name)
            self.assertEqual(course_name_scores[0].score, i+1)
        
        # Next update will make this name the default and pop it off the course name list
        c: models.AbstractCourse = self.dao_wrapper.update_course(code, name)
        self.assertEqual(c.name, name)
        course_name_scores: typing.List[models.CourseNameScore] = c.course_name_scores
        self.assertEqual( len(course_name_scores), 0) # Length should not change
    



if __name__ == '__main__':
    unittest.main()