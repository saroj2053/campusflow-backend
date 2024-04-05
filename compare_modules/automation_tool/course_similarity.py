from pymantic import sparql
from django.http import JsonResponse
import json
from compare_modules.sparql import get_course_uri_from_departments_and_university

def find_similarity_between_courses(data, other_university):
    try:
        department_name = data['belongs_to_department']
        course_language = data['has_language']
        program_type = data['belongs_to_program']
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

        # This query will return the results after filtering out courses with department, course language and program type university-wise
        qresponse = server.query(get_course_uri_from_departments_and_university(department_name, other_university,course_language, program_type))
        
        courses = qresponse['results']['bindings']
        course_data = {}

        for course in courses:
            course_uri = str(course['course']['value'])
            university_uri = str(course['university']['value'])
            # Store in dictionary
            course_data[course_uri] = university_uri

        compare_course_list = []
        for course_uri, university_uri in course_data.items():

            # Extract course name from the course URI
            course_name = course_uri.split('#')[1].rstrip('>')

            # Extract university name from the university URI
            university_name = university_uri.split('#')[1].rstrip('>')

            # Find the index where the university name ends
            index = course_name.find(university_name) + len(university_name)

            # Insert an underscore between university name and the rest of the course name
            compare_course_file_name = f"{university_name}_{course_name[index:]}"+".rdf"
            compare_course_list.append(compare_course_file_name)

        return compare_course_list
    except Exception as e:
        return JsonResponse({'message': f'Error during finding similarities between courses: {str(e)}'}, status=500)    
    