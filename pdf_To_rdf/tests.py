import os
import pdfplumber
import re
import json
import uuid
from rdflib import Graph, Literal, RDF, URIRef
from django.conf import settings

DATA_PATH = os.path.join(settings.BASE_DIR, 'RDF_DATA')
START_TXT = 'Anlage 2:'	
MODULE_NUMBER = 'Modulnummer'
MODULE_NAME = 'Modulname'
MODULE_CONTENT='Inhalte und Qualifikationsziele'
GRADES = 'Leistungspunkte und Noten'
WORKLOAD = 'Arbeitsaufwand'
LANGUAGE = 'Sprache'

class RdfUri:
    def __init__(self, module, course, uni, datatype_string, datatype_integer):
        self.module = module
        self.course = course
        self.uni=uni
        self.datatype_string = datatype_string
        self.datatype_integer = datatype_integer
class RePattern:
    def __init__(self, module_number_pattern, module_name_pattern, contents_pattern, teaching_language_pattern, credit_points_pattern, work_load_pattern):
        self.module_number_pattern = module_number_pattern
        self.module_name_pattern = module_name_pattern
        self.contents_pattern = contents_pattern
        self.teaching_language_pattern = teaching_language_pattern
        self.credit_points_pattern = credit_points_pattern
        self.work_load_pattern = work_load_pattern

class UniData():
    def __init__(self, rePattern, rdfUri, course_status):
        self.rePattern = rePattern
        self.rdfUri = rdfUri
        self.course_status = course_status

def get_uniData(course_status):
    if course_status['university_code'] == 'TUC':
        # Regular expressions to extract information
        rePattern = RePattern(re.compile(r'\nModulnummer\s+(.*?)\n', re.IGNORECASE | re.DOTALL),
                             re.compile(r"Modulname\s*(.+)"), 
                             re.compile(r'Inhalte:(.*?)(?=\nQualifikationsziele:|$)', re.DOTALL), 
                             re.compile(r'\nLehrformen\s+(.*?)\nVoraussetzungen für', re.IGNORECASE | re.DOTALL), 
                             re.compile(r'\nLeistungspunkte und.*?(\d+)', re.DOTALL),
                             re.compile(r'\nArbeitsaufwand.*?(\d+)(?=\s*AS|\s*\()', re.DOTALL))
        rdfUri = RdfUri('http://tuc.web.engineering/module#', 
                        'http://tuc/course#', 
                        'TUC', 
                        'http://www.w3.org/2001/XMLSchema#string', 
                        'http://www.w3.org/2001/XMLSchema#integer')
        return UniData(rePattern, rdfUri, course_status)
    else:
        rdfUri = RdfUri('http://tuc.web.engineering/module#', 
                        'http://tuc/course#', 
                        'BU', 
                        'http://www.w3.org/2001/XMLSchema#string', 
                        'http://www.w3.org/2001/XMLSchema#integer')
        rePattern = RePattern(re.compile(r"'Course code',\s*'([^']*)'"),
                             re.compile(r"'Course name', '([^']+)', 'Course code'"), 
                             re.compile(r"'Course content',\s*'([^']*)'"), 
                             "", 
                             re.compile(r"'No\. of ECTS(?: credits)?(?:\n)?credits', '([^']*)'"),
                             "")
        return UniData(rePattern, rdfUri, course_status)

def get_reqd_pages(pages):
     listofPage = []
     isStartPage = False
     for eachPage in pages:
        text = eachPage.extract_text()
        if START_TXT in text and MODULE_NUMBER in text and MODULE_NAME in text:
            isStartPage = True
        if isStartPage:
            listofPage.append(text)
     return listofPage 
  
## This code will convert pdf data to dictionary
def extract_text_from_pdf_tuc(pdf_path, uniData, end_page=None):
    with pdfplumber.open(pdf_path) as pdf_file: 
        pages = pdf_file.pages
        length = len(pages)
        # Ensure end_page is not greater than the total number of pages
        if end_page is None or end_page > length:
            end_page = length
            listofPage = get_reqd_pages(pages)
            moduleDict = {}
            result_list =[]
            for text in listofPage:
                if MODULE_NUMBER in text:
                    match = uniData.rePattern.module_number_pattern.search(text)
                    modulnummer = match.group(1).replace(' ', '')
                    moduleDict[modulnummer] = text
                else:
                     moduleDict[modulnummer] +=text
            for key, value in moduleDict.items():
                result_list.append(extract_information_tuc(key, value, uniData))  
            return result_list

def extract_text_from_pdf_bu(pdf_path, course_status, uniData, end_page=None):
 try:
    results = {}
    courseCode = course_status['course_code']   
    with pdfplumber.open(pdf_path) as pdf_file: 
        pages = pdf_file.pages
        length = len(pages)
        # Ensure end_page is not greater than the total number of pages
        if end_page is None or end_page > length:
            end_page = length
            result = {}
            if courseCode not in results:
                results[courseCode] = result
            for page in pages:
                table = page.extract_table()
                count = 0
                rowCount = 0
                if table is not None:
                    for row in table:
                        count += 1
                        filtered_list = [item for item in row if item is not None]       
                        filtered_list1 = [item for item in filtered_list if item != '']
                        rowStr = str(filtered_list1)
                        if MODULE_NAME not in result and rowCount > 0:
                            result[MODULE_NAME] = rowStr[2:-2]
                        number_match = re.search(uniData.rePattern.module_number_pattern, rowStr)
                        if number_match:
                            result[MODULE_NUMBER] = number_match.group(1).strip().replace(' ', '')
                            rowCount = count
                        name_match = re.search(uniData.rePattern.module_name_pattern, rowStr)
                        if name_match:
                            result[MODULE_NAME] = name_match.group(1).strip()

                        contents_match = re.search(uniData.rePattern.contents_pattern, rowStr)
                        if contents_match:
                            contents = contents_match.group(1).strip().replace('\\n', ' ')
                            result[MODULE_CONTENT] = ' '.join(contents.split())

                        if 'Course content' in rowStr and MODULE_CONTENT not in result:
                            pattern = r"\'Course content\', \"(.*)\"\]"
                            # Extracting content after "\'Course content\',"
                            match = re.search(pattern, rowStr)
                            if match:
                             contents = match.group(1).strip().replace('\\n', ' ')
                             result[MODULE_CONTENT] = ' '.join(contents.split())

                        if GRADES not in  rowStr and 'No. of ECTS' in rowStr:
                            split_string = rowStr.split(",")
                            last_element = split_string[-1].strip().strip("']")
                            if last_element.isdigit():
                                result[GRADES] = int(last_element)
                                result[WORKLOAD] = int(last_element) * 28
    return results
 except Exception as e:
     print(e)
        
# Function to extract information from a page
def extract_information_tuc(key, values, uniData):
    result ={}

    result[MODULE_NUMBER] = key
    # Extract Module Name
    match_module_name = uniData.rePattern.module_name_pattern.search(values)
    if match_module_name:
        result[MODULE_NAME] = match_module_name.group(1).strip()

    # Extract Contents
    match_contents = uniData.rePattern.contents_pattern.search(values)
    if match_contents:
        contents = match_contents.group(1)
        # Remove unwanted characters
        contents = contents.replace('Qualifikationsziele', '').replace('tionsziele', '').replace('ziele', '').strip().replace('\n', ' ')
        result[MODULE_CONTENT] =' '.join(contents.split())

    # #Extract Languages
    # match_lang =teaching_language_pattern.search(values)
    # if match_lang:
    #     contents = match_lang.group(1)
    #     if 'auch in englischer' in contents or 'deutscher oder in englischer' in contents:
    #          result[LANGUAGE] = ['German', 'English']
    #     elif 'Sprache' in contents:
    #             pattern = r'(\S+)\s+Sprache'
    #             # Find all matches of the pattern in the input text
    #             matches = re.findall(pattern, contents)
    #             if matches:
    #                  for key, value in langDict.items():
    #                      if value in matches[0]:
    #                          result[LANGUAGE] = [key]

    # if LANGUAGE not in result:
    #      result[LANGUAGE] = ['German'] # take German as default langugae
        
    # Extract Credit Points
    match_credit_points = uniData.rePattern.credit_points_pattern.search(values)
    if match_credit_points:
        result[GRADES] = match_credit_points.group(1).strip()
    
    # Extract Workload
    match_work_load = uniData.rePattern.work_load_pattern.search(values)
    if match_work_load:
        result[WORKLOAD] = match_work_load.group(1).strip()
    return result
   
def write_json(rdf_file_name, result_list) :
    output_json_path = os.path.join(DATA_PATH, f'{rdf_file_name}.json')
    try:
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json_data = json.dumps(result_list, indent=2, ensure_ascii=False)
            json_file.write(json_data)
            print(f"JSON data has been written to {output_json_path}")
            return json_data
    except Exception as e:
            print(e)
      
def write_rdf(data, course_status, rdf_file_name, uniData):
    try:
        # RDF Namespace
        module_ns = URIRef(uniData.rdfUri.module)
        # Create RDF graph
        g = Graph()
        # Iterate over each module in the JSON data
        for module in data:
            module_number = module.get(MODULE_NUMBER, "")
            module_name = module.get(MODULE_NAME, "")
            content = module.get(MODULE_CONTENT, "").replace("•","")
            langs = module.get(LANGUAGE, "")
            credit_points = module.get(GRADES, "")
            work_load = module.get(WORKLOAD, "")
            # Generate a UUID based on the current timestamp and node (hardware address)
            module_uuid = uuid.uuid1()

            # Convert the UUID to a string
            module_uuid_str = str(module_uuid)
            # RDF URI for the module
            module_uri = URIRef(f'{uniData.rdfUri.module}{module_uuid_str}')
            uni_uri= URIRef('http://across/university#')

            # Add RDF triples for the module
            g.add((module_uri, RDF.type, module_ns))
            g.add((module_uri, URIRef(f'{uniData.rdfUri.module}hasModuleNumber'), Literal(module_number, datatype=uniData.rdfUri.datatype_string)))
            g.add((module_uri, URIRef(f'{uniData.rdfUri.module}hasName'), Literal(module_name, datatype=uniData.rdfUri.datatype_string)))
            g.add((module_uri, URIRef(f'{uniData.rdfUri.module}hasContent'), Literal(content, datatype=uniData.rdfUri.datatype_string)))
        
        # for lang in langs:
        #     g.add((module_uri, URIRef(f'{URI_MODULE}hasLanguage'), Literal(lang, datatype=DATATYPE_STRING)))
   
        # Check if credit_points is non-empty before converting to integer
            if credit_points:
                try:
                    credit_points_value = int(credit_points)
                    g.add((module_uri, URIRef(f'{uniData.rdfUri.module}hasCreditPoints'), Literal(credit_points_value, datatype=uniData.rdfUri.datatype_integer)))
                except ValueError as ve:
                    print(f"Error converting credit_points to integer for module {module_name}: {ve}")

        # Check if work_load is non-empty before converting to integer
            if work_load:
                try:
                    work_load_value = int(work_load)
                    g.add((module_uri, URIRef(f'{uniData.rdfUri.module}hasWorkLoad'), Literal(work_load_value, datatype=uniData.rdfUri.datatype_integer)))
                except ValueError as ve:
                    print(f"Error converting work_load to integer for module {module_name}: {ve}")

                # Add additional RDF triples for each module
                g.add((module_uri, URIRef(f'{uni_uri}hasUniversity'), URIRef(f'{uni_uri}{uniData.rdfUri.uni}')))
                # single quotes are giving an error in 3.12 python
                g.add((module_uri, URIRef(f'{uniData.rdfUri.course}hasCourse'), URIRef(f'{uniData.rdfUri.course}{course_status["university_code"]}{course_status["course_code"]}')))

        # Serialize RDF graph to RDF/XML format
        rdf_outputBytes = (g.serialize(format="xml")).encode('utf-8')
    
        # Save RDF data to a file with proper encoding
        output_rdf_path = os.path.join(DATA_PATH, f'{course_status["university_name"].lower()}',  f'{rdf_file_name.lower()}.rdf')
        with open(output_rdf_path, "wb") as rdf_file:
            rdf_file.write(rdf_outputBytes)
            print(f"RDF data has been saved to {output_rdf_path}")
    except Exception as e:
            print(e)