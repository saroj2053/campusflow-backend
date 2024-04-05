from rdflib import URIRef, Literal
from rdflib.namespace import RDF, XSD
import json
from .sparql import *
from pymantic import sparql
from django.http import JsonResponse
import requests

def add_module_in_blaze(request):
     try:
        body = request.body.decode('utf-8')
        data = json.loads(body)
        courseUri = URIRef(data.get('courseUri',''))
        universityUri = URIRef(data.get('universityUri',''))
        moduleName = data.get('moduleName','')
        moduleContent = data.get('moduleContent','')
        moduleCreditPoints = data.get('moduleCreditPoints','')
        moduleId = data.get('moduleId','')
        print(data)
        server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql', post_queries=True, post_directly=True)
        
      
        uri_main = "http://tuc.web.engineering/module#"
        
        uri_end = ''.join(e for e in moduleId if e.isalnum())
        module_uri_g = URIRef(f"{uri_main}{uri_end}")
        uri_university = URIRef(universityUri)
        uri_course = URIRef(courseUri)
        module_name_g = Literal(moduleName, datatype=XSD.string)
        module_content_g = Literal(moduleContent, datatype=XSD.string)
        module_id_g = Literal(moduleId, datatype=XSD.string)
        credit_points_g = Literal(moduleCreditPoints, datatype=XSD.string)
      #   add_query_complete = add_module % (module_uri_g ,module_id_g, module_name_g , module_content_g, credit_points_g,uri_university, uri_course)
        print(add_module(module_uri_g, module_id_g, module_name_g, module_content_g, credit_points_g, uri_course, uri_university))
        payload = {'update': add_module(module_uri_g, module_id_g, module_name_g, module_content_g, credit_points_g, uri_course, uri_university)}
        
        result = requests.post("http://16.171.152.55/blazegraph/namespace/kb/sparql", data=payload)
        print(result)
      #   print(add_module % (module_uri_g , module_uri_g ,module_id_g))
        
      #   result = server.update(add_module % (module_uri_g ,module_id_g, module_name_g , module_content_g, credit_points_g,uri_university, uri_course))
      #   result = server.query(add_module % (module_uri_g , module_uri_g ,module_id_g ))
      #   server.update(f"load {result}")
        return JsonResponse({'message': 'Module added successfully', 'uri': module_uri_g}, status=200)
     except Exception as e:
        return JsonResponse({'message': f'Error adding module: {str(e)}'}, status=500)

     
        