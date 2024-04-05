import urllib.request
import ssl
from bs4 import BeautifulSoup
from rdflib import Namespace
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD
import re
import PyPDF2
import wget
from os import listdir
from os.path import isfile, join

courses_list = {'Computer Science': 'http://tuc/course#BUMSCS', 'Architecture': 'http://tuc/course#BUMA', 'Electrical Engineering': 'http://tuc/course#BUME', 'Mechanical Engineering': 'http://tuc/course#BUMM', 'Civil Engineering and Environmental Sciences': 'http://tuc/course#BUCE', 'Engineering Management': 'http://tuc/course#BUEM', 'Civil and Earth Sciences': 'http://tuc/course#BUCES', 'Biomedical Engineering': 'http://tuc/course#BUCBE'}

CIVIL_EARTH_SCIENCES_V1 = "Civil Engineering and Environmental Sciences"
CIVIL_EARTH_SCIENCES_V2 = "Civil Engineering and Envir onmental Sciences"
CIVIL_EARTH_SCIENCES_V3 = "Civil and Environmental Science"
CIVIL_EARTH_SCIENCES_V4 = "Civil Engineering and Environmental Science"
CIVIL_EARTH_SCIENCES_V5 = "Civil and Environmental Sciences"
ENGINEERING_MANAGEMENT_V2 = "Engineering Managment"
ENGINEERING_MANAGEMENT_V1 = "Engineering Management"
ENGINEERING_MANAGEMENT_V3 = "Faculty of Engineering Management"
MECHINICAL_ENGINEERING_V1 = "Mechanical Engineering"
MECHINICAL_ENGINEERING_V2 = "Faculty of Mechanical Engineering"
COMPUTER_SCIENCE = "Computer Science"
ARCHITECTURE = "Architecture"
BIOMEDICAL_ENGINEERING = "Biomedical Engineering"
CIVIL_ENGINEERING = "Civil and Earth Sciences"
ELECTRICAL_ENGINEERING = "Electrical Engineering"

added_module_names = set()
special_case_modules = {'Forest pathology': "IS-FF-00036S",'Computer modeling of water supply and sewage systems': "IS-FCEE-00133W", 'Forest hydrology': "IS-FF-00011W", 'Chemistry': "IS-FF-00001W", 'Invasive species in forest areas': "S-FF-00042W/S", 'Forest mushrooms in medicine': "IS-FF-00043S", 'Heating systems': "FCEE-00077W", 'Water management and water protection': "IS-FCEE-00134W", 'Forest protection': "IS-FF-00037S", 'Air conditioning and ventilation systems 2': "FCEE-00108W", 'Forest management in valuable natural areas': "IS-FF-00041W/S", 'Natural medicinal substances m forest materialsfro': "IS-FF-00044S", 'Air conditioning and Ventilation systems 1': "FCEE-00107W", 'Technology and organization of sanitary works': "IS-FCEE-00213W", 'Biodiversity conservation of forest areas': "IS-FF-00038-1W/S", 'Forest botany: Dendrology': "IS-FF-00032W/S", 'Forest applied botany': "IS-FF-00025W/S" , 'Heat centers': "FCEE-00143W"}

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

namespace_manager = graph.namespace_manager
uri_main = "http://tuc.web.engineering/module#"
ns_module = Namespace(uri_main)

base_url = "https://usos-ects.uci.pb.edu.pl/"
try:
 _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
 pass
else:
     ssl._create_default_https_context = _create_unverified_https_context
    


# Download all pdfs of modules only once to be called
     
# html = urllib.request.urlopen("https://pb.edu.pl/erasmus-course-catalogue/?sem&f=faculty-of-computer-science&ects")
# data = html.read()
# parser = BeautifulSoup(data, 'html.parser')
# all_thbody_tr = parser.find_all("tr")
# for module in all_thbody_tr:
#    all_list_a = module.find_all("a" ,limit=1)
#    for a in all_list_a:
#      pdf_url = a.get("href")
#      print(pdf_url)
#     #  pdf = urllib.request.urlopen(pdf_url)
#      count = 0
#      wget.download(pdf_url)
#    break 
    #  print(pdf.read())



field_of_study_pattern = re.compile(r'(?<=Faculty of )(.*?)(?= Field of study)')
field_of_study_pattern_v2 = re.compile(r'(?<=Field of study )(.*?)(?= Degree level)')
programme_type_pattern = re.compile(r'(?<=and programme type)(.*?)(?= Specialization/)')
course_name_pattern = re.compile(r'(?<=Course name)(.*?)(?= Course code)')
course_code_pattern = re.compile(r'(?<=Course code)(.*?)(?= Course type)')
course_code_pattern_2 = re.compile(r'(?<=L1P_U06)(.*?)(?= LO4)')
ects_pattern = re.compile(r'(?<=No. of ECTS credits)(.*?)(?= Entry)')
credit_hours_pattern = re.compile(r'(?<=TOTAL:)(.*?)(?= Quantitative)')
content_pattern = re.compile(r'(?<=Course content)(.*?)(?=Teaching methods)')

BASE_URL = "some_merged_modules.pdf"
departments = set()

pdf_file = open(f"{BASE_URL}", "rb")  
pdf_reader = PyPDF2.PdfReader(pdf_file)
noOfPages = len(pdf_reader.pages)
    
for pageNo in range(noOfPages):
    print(pageNo)
    page = pdf_reader.pages[pageNo]
    text = page.extract_text()
    text = " ".join(text.split())
    print(text)
    field_of_study = field_of_study_pattern.search(text)
    field_of_study_v2 = field_of_study_pattern_v2.search(text)
    programme_type = programme_type_pattern.search(text)
    course_name = course_name_pattern.search(text)
    course_code = course_code_pattern.search(text)
    ects = ects_pattern.search(text)
    hours = credit_hours_pattern.search(text)
    content = content_pattern.search(text)
    
    field_of_study_v = ""
    programme_type_v = ""
    course_name_v = ""
    course_code_v = ""
    ects_v = ""
    hours_v = ""
    content_v = ""
    
    if field_of_study:
        field_of_study_v = field_of_study.group(1).strip()
        print(field_of_study)
        if field_of_study_v:
            if field_of_study_v == CIVIL_EARTH_SCIENCES_V1 or field_of_study_v == CIVIL_EARTH_SCIENCES_V2 or field_of_study_v == CIVIL_EARTH_SCIENCES_V3 or field_of_study_v == CIVIL_EARTH_SCIENCES_V4 or field_of_study_v == CIVIL_EARTH_SCIENCES_V5:
             departments.add(CIVIL_EARTH_SCIENCES_V1)
            elif field_of_study_v == ENGINEERING_MANAGEMENT_V1 or field_of_study_v == ENGINEERING_MANAGEMENT_V2 or field_of_study_v == ENGINEERING_MANAGEMENT_V3:
             departments.add(ENGINEERING_MANAGEMENT_V1) 
            elif field_of_study_v == MECHINICAL_ENGINEERING_V1 or field_of_study_v == MECHINICAL_ENGINEERING_V2:
             departments.add(MECHINICAL_ENGINEERING_V1)  
            else:
             departments.add(field_of_study_v)
        else :
           field_of_study_v = field_of_study_v2.group(1).strip()

    else:
        if field_of_study_v2:
           field_of_study_v = field_of_study_v2.group(1).strip()
           departments.add(field_of_study_v)
           print(field_of_study_v)

    if programme_type:
        programme_type_v = programme_type.group(1).strip()
    else:
        print("No match found for programme.")

    if course_name:
        course_name_v = course_name.group(1).strip()
    else:
        print("No match found for course name.")

    if course_code:
        course_code_v = course_code.group(1).strip()
        if course_code_v == "":
            print(course_name_v)
            value = special_case_modules.get(course_name_v)
            if value:
             course_code_v = value
            print(course_code_v)

    if ects:
        ects_v = ects.group(1).strip()
    else:
        print("No match found for ects")


    if hours:
        hours_v = hours.group(1).strip()
        if hours_v == "": 
            if ects_v:
                to_int = int(ects_v)
                if(to_int):
                    hours_v = to_int * 28; 

    else:
        if ects_v:
                to_int = int(ects_v)
                if(to_int):
                    hours_v = to_int * 28; 

    if content:
        content_v = content.group().strip()
    else:
        print("No match found for content")

    if field_of_study_v and field_of_study_v == ARCHITECTURE:
        print("value of field of study:"+field_of_study_v)
        module_uri_g = URIRef(f"{uri_main}{''.join(e for e in course_code_v if e.isalnum())}")
        uriUniversity = URIRef("http://across/university#BU")
        uriCourse = URIRef(courses_list.get(field_of_study_v))
        module_name_g = Literal(course_name_v, datatype=XSD.string)
        module_content_g = Literal(content_v, datatype=XSD.string)
        module_id_g = Literal(course_code_v, datatype=XSD.string)
        credit_points_g = Literal(ects_v, datatype=XSD.string)
        hours_g = Literal(hours_v, datatype=XSD.string)
        language_g = Literal("English", datatype=XSD.string)
        programme_type_g = Literal(programme_type_v, datatype=XSD.string)
        department_g = Literal(field_of_study_v, datatype=XSD.string)
            
        if course_name_v!="" and module_name_g not in added_module_names and not is_module_name_in_graph(graph, module_name_g):
            graph.add((module_uri_g, RDF.type, NAME_SPACE.module))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasName"), module_name_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasLanguage"), language_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasProgrammeType"), programme_type_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasWorkLoad"), hours_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasModuleNumber"), module_id_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasContent"), module_content_g))
            graph.add((module_uri_g, URIRef("http://tuc.web.engineering/module#hasCreditPoints"), credit_points_g))
            graph.add((module_uri_g, URIRef("http://tuc/course#hasCourse"), uriCourse))
            graph.add((module_uri_g, URIRef("http://tuc/dept#hasDept"), department_g))
            graph.add((module_uri_g, URIRef("http://across/university#hasUniversity"), uriUniversity))
        # if(count > 0): 
        #     break
    

bialystok_modules_data = graph.serialize(format='xml')
with open('data_me.rdf', 'w', encoding='utf-8') as bialystok_modules_file:
    bialystok_modules_file.write(bialystok_modules_data)
bialystok_modules_file.close()

print(departments)


