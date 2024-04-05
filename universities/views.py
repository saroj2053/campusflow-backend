from django.shortcuts import render
from pymantic import sparql
from .sparql import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@csrf_exempt
@require_GET
def get_universities(request):
    try:
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

        qresponse = server.query(university_list_query)
        data = []
        data_list = qresponse['results']['bindings']
        
        for row in data_list:
            data_dict = {
                'id': str(row['hasUniversityId']['value']),
                'name': str(row['universityName']['value']),
                'uri': str(row['university']['value']),
            }
            data.append(data_dict)
        return JsonResponse(data , safe=False)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)
