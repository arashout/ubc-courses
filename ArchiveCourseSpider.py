from bs4 import BeautifulSoup
import requests
import re
import json
import time

with open('current_courses.json', 'r') as f:
    current_course_dict = json.load(f)

url_subject_index = r'http://www.calendar.ubc.ca/vancouver/courses.cfm?page=name'
url_base = r'http://www.calendar.ubc.ca/vancouver/'

response = requests.get(url_subject_index)
soup_index = BeautifulSoup(response.content, 'html.parser')
trs = soup_index.find_all('tr', {'class': 'row-highlight'})
subject_links = [tr.a['href'] for tr in trs]

re_course_code = re.compile(r"(.*)\s\(")
re_course_name = re.compile(r"\)\s(.*)")

for subject_link in subject_links:
    response = requests.get(url_base + subject_link)
    soup_subject = BeautifulSoup(response.content, 'html.parser')
    dts = soup_subject.find_all('dt')
    for dt in dts:
        course_text = dt.get_text()
        course_code = re.findall(re_course_code, course_text)[0]
        course_name = re.findall(re_course_name, course_text)[0]
        if current_course_dict.get(course_code) is None:
            current_course_dict[course_code] = course_name
            print('{0} : {1} Added'.format(course_code, course_name))

    time.sleep(5)
with open('all_courses.json', 'w') as f:
    json.dump(current_course_dict, f)
