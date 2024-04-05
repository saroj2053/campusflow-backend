import rdflib
import json
from .sparql import *
from os import listdir
from os.path import isfile, join


def find_all_similar_modules_list():
    graph = rdflib.Graph()
    onlyfiles = [f for f in listdir("RDF_DATA/Refined_RDF_DATA") if isfile(join("RDF_DATA/Refined_RDF_DATA", f))]
    for file in onlyfiles:
        graph.parse(f"RDF_DATA/Refined_RDF_DATA/{file}")
    
    graph.parse("RDF_DATA/universities.rdf")
    graph.parse("RDF_DATA/tuc_courses.rdf")
    qresponse = graph.query(list_with_similar_modules_query)
    data_list = []
    for row in qresponse:
        data_dict = {
            'id': str(row.moduleId),
            'name': str(row.moduleName),
            'content': str(row.moduleContent),
            'creditPoints': str(row.moduleCreditPoints),
            'university': str(row.universityName),
            'courseName': str(row.courseName),
            'similarModuleId': str(row.similarModuleId),
            'similarModuleName': str(row.similarModuleName),
            'similarModuleContent': str(row.similarModuleContent),
            'similarModuleCreditPoints': str(row.similarModuleCreditPoints),
            'similarUniversity': str(row.universityNameSimilar),
            'courseNameSimilar': str(row.courseNameSimilar),
        }
        data_list.append(data_dict)
    json_data = json.dumps(data_list, indent=2)
    return json_data
