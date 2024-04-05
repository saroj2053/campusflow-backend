import rdflib
from pymantic import sparql
from .sparql import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def get_courses_from_university(request):
    # Get the raw request body
    body = request.body.decode('utf-8')

    try:
        # Parse JSON data from the request body
        data = json.loads(body)
        universityName = data.get('universityName','')
        universityUri = data.get('universityUri','')

        # SPARQL query to retrieve university names and course names
        sparql_query = get_course_from_university_query(universityUri, universityName)

        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

        qresponse = server.query(sparql_query)
        course_list = []
        data = qresponse['results']['bindings']
        
        # Process the results
        for result in data:
            course_list_temp = {
                'courseUri' :  str(result['courseUri']['value']),
                'courseName' : str(result['courseName']['value']),
                'courseNumber' : str(result['courseNumber']['value'])
            }
            course_list.append(course_list_temp)

        # Return JSON response
        if not course_list:
            response = {
                "message": f"No courses found for {universityName}, please check university uri or university name",
                "university": universityName
            }
            return JsonResponse(response, status =404)
        else:
            response = {
                "message": "Course list returned successfully",
                "courses": course_list,
                "university": universityName
            }
            return JsonResponse(response, status =200)

    except json.JSONDecodeError as json_error:
        response = {
            "message": f"JSON decoding error: {json_error}"
        }
        return JsonResponse(response, status =400)
    except rdflib.exceptions.Error as rdf_error:
        response = {
            "message": f"RDF parsing error: {rdf_error}"
        }
        return JsonResponse(response, status =500)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)
