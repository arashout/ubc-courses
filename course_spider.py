import requests
import sqlite3
from lxml import etree
from typing import List
import time
import DatabaseWrapper


URL_UBC_BASE = r'https://courses.students.ubc.ca'
URL_SUBJECT_INDEX = r'https://courses.students.ubc.ca/cs/main?pname=subjarea'

XPATH_SUBJECT = r"//table[@id='mainTable']//tbody//tr//td//a"
XPATH_COURSE_CODE = r"//table[@id='mainTable']//tbody//tr//td//a"
XPATH_COURSE_NAME = r"//table[@id='mainTable']//tbody//tr//td[2]"

def get_course_codes_and_names(subject_link: str, parser) -> List[tuple]:
    """
    Python docs
    """
    response = requests.get(subject_link)
    html_tree = etree.fromstring(response.content, parser)
    elements_course_codes = html_tree.xpath(XPATH_COURSE_CODE)
    elements_course_names = html_tree.xpath(XPATH_COURSE_NAME)
    assert(len(elements_course_codes) == len(elements_course_names))
    return zip(elements_course_codes, elements_course_names)

def crawl() -> List[tuple]:
    response = requests.get(URL_SUBJECT_INDEX)
    html_parser = etree.HTMLParser()
    tree = etree.fromstring(response.content, html_parser)
    subject_links = tree.xpath(XPATH_SUBJECT)
    subject_links = [(URL_UBC_BASE + link.attrib['href']) for link in subject_links]

    course_code_name_list = []

    for subject_link in subject_links:
        for t in get_course_codes_and_names(subject_link, html_parser):
            course_code = t[0].text
            course_name = t[1].text
            course_tuple = (course_code, course_name)
            print( course_tuple )
            course_code_name_list.append( course_tuple )
            return course_code_name_list
        time.sleep(1)

    return course_code_name_list
if __name__ == "__main__":
    courses_tuple_list = crawl()
    db_wrapper = DatabaseWrapper.DatabaseWrapper()
    db_wrapper.save_courses(courses_tuple_list)
    db_wrapper.close()

