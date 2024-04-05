from adminapp import sparql as sparqlquery
from pymantic import sparql
from .sparql import *
import requests
from django.http import JsonResponse
import shortuuid
import re

def create_course_entry_in_rdf(data):
    
    course_name = data.get('courseName','')
    belongs_to_university = data.get('belongsToUniversity','')
    belongs_to_program = data.get('belongsToProgram','')
    belongs_to_department = data.get('belongsToDepartment','')
    has_language = data.get('hasLanguage','')

    course_uri = ''
    university_uri=''
    server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

    # Generate a short UUID
    short_uuid = shortuuid.uuid()
    # Remove alphabets from the short UUID
    uuid_numeric_only = re.sub(r'[^0-9]', '', short_uuid)
    # Getting University URI
    qresponse = server.query(sparqlquery.get_university_uri_by_university_name(belongs_to_university))
    data_for_unviersity_uri = qresponse['results']['bindings'] 
    for result in data_for_unviersity_uri:
        university_uri = str(result['universityUri']['value'])
    university_code = university_uri.split('#')[1]

    # Validating Course URI does it already exist or not
    query = sparqlquery.get_course_uri_by_course_and_university_name(course_name, belongs_to_university)
    qresponse = server.query(query)
    data_for_course_uri = qresponse['results']['bindings'] 
    for result in data_for_course_uri:
        course_uri = str(result['courseUri']['value'])
    
    if course_uri:                              # It means rdf entry for course already exist
         # Extract course name from the course URI
        course_name = course_uri.split('#')[1].rstrip('>')

        # Extract university name from the university URI
        university_name = university_uri.split('#')[1].rstrip('>')

        # Find the index where the university name ends
        index = course_name.find(university_name) + len(university_name)

        # Insert an underscore between university name and the rest of the course name
        rdf_file_path = f"{university_name}_{course_name[index:]}"
        course_code = course_uri.split('#')[1]
        response_data = {
                        'message': "Given Course already exist",
                        'university_name': belongs_to_university,
                        'university_code': university_code,
                        'course_code': course_code,
                        'belongs_to_department': belongs_to_department,
                        'course_name': course_name,
                        'course_uri': course_uri,
                        'belongs_to_program': belongs_to_program,
                        'has_language': has_language,
                        'rdf_file_path': rdf_file_path,
                        'status': True
                    }
        return response_data
    else:
        course_code = course_name.replace(' ','')
        course_uri = "http://tuc/course#"+university_code+course_code

    payload = {'update': add_course(uuid_numeric_only, course_uri, course_name, belongs_to_program, belongs_to_department, university_uri,has_language)}
        
    result = requests.post("http://16.171.152.55/blazegraph/namespace/kb/sparql", data=payload)
    
    if result.status_code == 200:
        response_data = {
                        'message': "New Course Entry Created in our database",
                        'university_name': belongs_to_university,
                        'university_code': university_code,
                        'course_code': course_code,
                        'belongs_to_department': belongs_to_department,
                        'course_name': course_name,
                        'course_uri': course_uri,
                        'belongs_to_program': belongs_to_program,
                        'has_language': has_language,
                        'status': False
                    }
        return response_data
    else:
        response_data = {
                        'message': "Error occured in creation of new course entry",
                    }
        return response_data