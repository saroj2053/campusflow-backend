import rdflib
from pymantic import sparql
from .sparql import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

@csrf_exempt
@require_GET
def list_similar_modules(request):
    try:
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

        qresponse = server.query(list_with_similar_modules_query)
        data_list = []
        
        # Assuming 'data' is a list of dictionaries
        for row in qresponse['results']['bindings']:
            data_dict = {
                'id': row['sampleModuleId']['value'],
                'name': row['sampleModuleName']['value'],
                'content': row['sampleModuleContent']['value'],
                'creditPoints': row['sampleModuleCreditPoints']['value'],
                'university': row['sampleUniversity']['value'],
                'courseName': row['sampleCourse']['value'],
                'similarModuleId': row['sampleSimilarModuleId']['value'],
                'similarModuleName': row['sampleSimilarModuleName']['value'],
                'similarModuleContent': row['sampleSimilarModuleContent']['value'],
                'similarModuleCreditPoints': row['sampleSimilarModuleCreditPoints']['value'],
                'similarUniversity': row['sampleSimilarUnivserity']['value'],
                'courseNameSimilar': row['sampleSimilarCourse']['value'],
            }
            data_list.append(data_dict)

        return JsonResponse(data_list, safe=False, json_dumps_params={'indent': 2})

    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status=500)


@csrf_exempt
def get_similar_module_against_given_module_uri(request):
    try:
        moduleUri = request.GET.get('moduleUri', '')
        moduleName = ''
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')
        uniqueResults = set()
        # Fetch Module Name from Module Details
        module_details = server.query(get_module_details_from_module_uri(moduleUri))
        data = module_details['results']['bindings']
        for row in data:
            moduleName = str(row['moduleName']['value'])
            break

        qresponse = server.query(get_similar_module_against_module_uri_query(moduleUri))
        similar_module_list = []
        data = qresponse['results']['bindings']
        for row in data:
            key = f"{str(row['moduleName']['value'])}{str(row['similarModuleName']['value'])}"
            if(key not in uniqueResults):
                uniqueResults.add(key)
                data_dict = {
                'id': str(row['moduleId']['value']),
                'name': str(row['moduleName']['value']),
                'content': str(row['moduleContent']['value']),
                'creditPoints': str(row['moduleCreditPoints']['value']),
                'university': str(row['universityName']['value']),
                'courseName': str(row['courseName']['value']),
                'similarModuleId': str(row['similarModuleId']['value']),
                'similarModuleName': str(row['similarModuleName']['value']),
                'similarModuleContent': str(row['similarModuleContent']['value']),
                'similarModuleCreditPoints': str(row['similarModuleCreditPoints']['value']),
                'similarUniversity': str(row['universityNameSimilar']['value']),
                'courseNameSimilar': str(row['courseNameSimilar']['value']),
                
                'similarModuleWorkLoad': str(row['similarModuleWorkLoad']['value']),
                'similarMouleLanguage': str(row['similarMouleLanguage']['value']),
                'similarModuleProgram': str(row['similarModuleProgram']['value']),
                'similarModuleDepartment': str(row['similarModuleDepartment']['value']),

                'moduleUri': str(row['module']['value']),
                'similarModuleUri': str(row['similarModule']['value']),
                }
                similar_module_list.append(data_dict)

        # Return JSON response
        if not similar_module_list:
            response = {
                "message": f"No similar modules found for module named as <strong>{moduleName}</strong>.",
                "moduleUri": moduleUri,
                "moduleName": moduleName
            }
            return JsonResponse(response, status =404)
        else:
            response = {
                "message": "Similar module list returned successfully",
                "modules": similar_module_list,
                "moduleUri": moduleUri
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

@csrf_exempt
@require_POST
def get_modules_from_course_and_university(request):
    # Get the raw request body
    body = request.body.decode('utf-8')

    try:
        # Parse JSON data from the request body
        data = json.loads(body)
        courseUri = data.get('courseUri','')
        universityUri = data.get('universityUri','')
        courseName = data.get('courseName','')
     
        # SPARQL query to retrieve university names and course names
        sparql_query = get_modules_from_course_and_university_query(courseUri, courseName, universityUri)

        # Execute the SPARQL query
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

        qresponse = server.query(sparql_query)
        module_list = []
        data = qresponse['results']['bindings']
        # Process the results
        for result in data:
            module_list_temp = {
                'moduleUri' :  str(result['moduleUri']['value']),
                'moduleName' : str(result['sampleModuleName']['value']),
                'moduleNumber' : str(result['sampleModuleNumber']['value']),
                'moduleContent' : str(result['sampleModuleContent']['value']),
                'moduleCreditPoints' : str(result['sampleModuleCreditPoints']['value'])
            }
            module_list.append(module_list_temp)

        # Return JSON response
        if not module_list:
            response = {
                "message": f"No modules found for course named as {courseName}, please check university uri or course uri or course name",
                "course": courseName
            }
            return JsonResponse(response, status =404)
        else:
            response = {
                "message": "Module list returned successfully",
                "modules": module_list,
                "course": courseName
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

@csrf_exempt
@require_GET
def get_all_modules(request):
    try:
        server = sparql.SPARQLServer('http://192.168.0.102:9999/bigdata/sparql')

        qresponse = server.query(get_all_modules_query())
        data_list = []
        
        # Assuming 'data' is a list of dictionaries
        for row in qresponse['results']['bindings']:
            data_dict = {
                'module_uri': row['moduleUri']['value'],
                'module_number': row['sampleModuleNumber']['value'],
                'module_name': row['sampleModuleName']['value'],
                'module_content': row['sampleModuleContent']['value'],
                'module_credit_points': row['sampleModuleCreditPoints']['value'],
                'module_workload': row['sampleModuleWorkLoad']['value'],
                'belongs_to_university': row['sampleUniversityName']['value'],
                'belongs_to_course': row['sampleCourseName']['value'],
                'belongs_to_program': row['sampleModuleBelongsToProgram']['value'],
                'belongs_to_department': row['sampleModuleBelongsToDepartment']['value'],
                'has_language': row['sampleModuleHasLanguage']['value']
            }
            data_list.append(data_dict)

        return JsonResponse(data_list, safe=False, json_dumps_params={'indent': 2})
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)


@csrf_exempt
@require_GET
def get_searched_modules(request):
    search_term = request.GET.get('queryTerm', '')
    try:
        
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')
        searchedResponse = server.query(get_searched_modules_query(search_term))

        retrievedModules_list = []
        for row in searchedResponse['results']['bindings']:
            searched_modules = {
                'module_uri': row['moduleUri']['value'],
                'module_number': row['sampleModuleNumber']['value'],
                'module_name': row['sampleModuleName']['value'],
                'module_content': row['sampleModuleContent']['value'],
                'module_credit_points': row['sampleModuleCreditPoints']['value'],
                'module_workload': row.get('sampleModuleWorkLoad', {}).get('value', ''),
                'belongs_to_university': row['sampleUniversityName']['value'],
                'belongs_to_course': row['sampleCourseName']['value'],
                'belongs_to_program': row['sampleModuleBelongsToProgram']['value'],
                'belongs_to_department': row['sampleModuleBelongsToDepartment']['value'],
                'has_language': row['sampleModuleHasLanguage']['value']
            }
            retrievedModules_list.append(searched_modules)

        return JsonResponse(retrievedModules_list, safe=False, json_dumps_params={'indent': 2})
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status=500)

@csrf_exempt
@require_GET
def get_module_details(request):
    moduleUri = request.GET.get('moduleUri', '')
    try:
        
        server = sparql.SPARQLServer('http://192.168.0.102:9999/bigdata/sparql')
        retrievedModuleDetails = server.query(get_module_details_query(moduleUri))

        retrievedModuleDetails_list = []
        for row in retrievedModuleDetails['results']['bindings']:
            moduleDetails_dict = {
                'module_uri': row['moduleUri']['value'],
                'module_number': row['moduleNumber']['value'],
                'module_name': row['moduleName']['value'],
                'module_content': row['moduleContent']['value'],
                'module_credit_points': row['moduleCreditPoints']['value'],
                'module_workload': row.get('moduleWorkLoad', {}).get('value', ''),
                'belongs_to_university': row['universityName']['value'],
                'belongs_to_course': row['courseName']['value'],
                'belongs_to_program': row['courseProgram']['value'],
                'belongs_to_department': row['courseBelongsToDepartment']['value'],
                'has_language': row['courseHasLanguage']['value']
            }
            retrievedModuleDetails_list.append(moduleDetails_dict)

        return JsonResponse(retrievedModuleDetails_list, safe=False, json_dumps_params={'indent': 2})
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status=500)