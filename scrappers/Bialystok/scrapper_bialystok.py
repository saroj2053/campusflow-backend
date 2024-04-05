import urllib.request
import ssl
from bs4 import BeautifulSoup
from rdflib import Namespace
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD
import re

added_module_names = set()

def is_module_name_in_graph(graph, module_name_g):
    # Convert module name to lowercase for case-sensitive check
    normalized_module_name_g = module_name_g.lower()

    # Query the graph for modules with the same name
    for triple in graph.triples((None, URIRef("http://tuc.web.engineering/module#hasName"), None)):
        if normalized_module_name_g == str(triple[2]).lower():
            return True
    return False

graph = Graph()

NAME_SPACE = Namespace("http://tuc.web.engineering/")
NAME_SPACE.module

# namespace_manager = graph.namespace_manager
uri_main = "http://tuc.web.engineering/module#"
# ns_module = Namespace(uri_main)
DEPARTMENT_CS = "Faculty of Computer Science"
DEPARTMENT_FOREIGN_LC = "Foreign Language Centre"
DEPARTMENT_ENGINEERING_MANAGEMENT = "Faculty of Engineering Management"
DEPARTMENT_MECHINICAL_ENGINEERING = "Faculty of Mechanical Engineering"
DEPARTMENT_CIVIL_ENGINEERING = "Faculty of Civil Engineering and Environmental Sciences"
DEPARTMENT_ELECTRICAL_ENGINEERING = "Faculty of Electrical Engineering"

base_url = "https://usos-ects.uci.pb.edu.pl/"
try:
 _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
 pass
else:
     ssl._create_default_https_context = _create_unverified_https_context
    
pages = [0 ,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# pages = [0]

for page in pages:
    html = urllib.request.urlopen(f"{base_url}en/courses/list?page={page}")
    data = html.read()
    parser = BeautifulSoup(data, 'html.parser')
    all_list_a = parser.find_all("a")
    module_id_list = []
    for course in all_list_a:
     print("connecting: "+str(page))
     url = course.get("href")
     if('/en/courses/view?prz_kod=' in url):
        module_id_list.append(url)

    count = 0
    for id_url in module_id_list:
     course_data_html = urllib.request.urlopen(f"{base_url}{id_url}")
     data_courses = course_data_html.read()
     parser_courses = BeautifulSoup(data_courses, 'html.parser')
     module_name = parser_courses.find("h1").getText().split("\n")
     module_name_value = module_name[1].lstrip(' ')
     module_id =  id_url.split("=")[1]
     module_content = parser_courses.find("div", class_="opis iml").getText()
     credit_points = parser_courses.find("div", class_="item punkty_ects")
     department = parser_courses.find("div", class_="item jednostka").find("a").getText()
     credit_points_value = credit_points.getText()
     credit_points_value_number = re.findall("\d+", credit_points_value)
     credit_points_value_to_be_added = credit_points_value_number[0]  if(len(credit_points_value_number)) > 2 else 6
     
     uri_end = ''.join(e for e in module_id if e.isalnum())
     print(uri_end)
     if(uri_end!="None" and uri_end!="inPolish" and department == DEPARTMENT_CIVIL_ENGINEERING):
        print(f"{base_url}{id_url}")
        module_uri_g = URIRef(f"{uri_main}{uri_end}")
        uriUniversity = URIRef("http://across/university#BU")
        uriCourse = URIRef("http://tuc/course#Civil_Engineering_and_Environmental_Sciences")
        module_name_g = Literal(module_name_value, datatype=XSD.string)
        module_content_g = Literal(module_content, datatype=XSD.string)
        module_id_g = Literal(module_id, datatype=XSD.string)
        credit_points_g = Literal(credit_points_value_to_be_added, datatype=XSD.string)
        department_g = Literal(department, datatype=XSD.string)
        university_g = Literal("", datatype=XSD.string)
        
        if module_name_g not in added_module_names and not is_module_name_in_graph(graph, module_name_g):
            graph.add((module_uri_g, RDF.type, NAME_SPACE.module))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasName"), module_name_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasModuleNumber"), module_id_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasContent"), module_content_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasCreditPoints"), credit_points_g))
            graph.add((module_uri_g, URIRef("http://tuc/course#hasCourse"), uriCourse))
            graph.add((module_uri_g, URIRef("http://across/university#hasUniversity"), uriUniversity))
        
bialystok_modules_data = graph.serialize(format='xml')
with open('bu_Civil_Engineering_and_Environmental_Sciences.rdf', 'w', encoding='utf-8') as bialystok_modules_file:
    bialystok_modules_file.write(bialystok_modules_data)
bialystok_modules_file.close()
    
html.close()

