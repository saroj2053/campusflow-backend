university_list_query = """
SELECT ?universityName ?hasUniversityId ?university
WHERE {
    ?university <http://across/university#hasUniversityName> ?universityName ;
            <http://across/university#hasUniversityId> ?hasUniversityId .
}
"""


# add_module = """INSERT DATA { <%s> rdf:type <http://tuc.web.engineering/module#> .
#                               <%s> <http://tuc.web.engineering/module#hasModuleNumber>  %s .
#                              }
# """
# add_module_1 = """ INSERT DATA { <http://tuc.web.engineering/module#jhlkh1> rdf:type <http://tuc.web.engineering/module#> .
#              <http://tuc.web.engineering/module#jhlkh1> <http://tuc.web.engineering/module#hasModuleNumber>  789 .
#             }
                             
# """
# add_module = """INSERT DATA { <%s> rdf:type <http://tuc.web.engineering/module#> ;
#                                    <http://tuc.web.engineering/module#hasModuleNumber>  <%s> ;
#                                    <http://tuc.web.engineering/module#hasName>  <%s> ;
#                                    <http://tuc.web.engineering/module#hasContent>  <%s> ;
#                                    <http://tuc.web.engineering/module#hasCreditPoints>  <%s> ;
#                                    <http://across/university#hasUniversity>  <%s> ;
#                                    <http://tuc/course#hasCourse>  <%s> . }
# """


def add_module(moduleUri, moduleNumber, moduleName, moduleContent, modulePoints, courseUri, universityUri):
    query = f"""
        INSERT DATA {{ <{moduleUri}> rdf:type <http://tuc.web.engineering/module#> ;
                                   <http://tuc.web.engineering/module#hasModuleNumber>  "{moduleNumber}" ;
                                   <http://tuc.web.engineering/module#hasName>  "{moduleName}" ;
                                   <http://tuc.web.engineering/module#hasContent>  "{moduleContent}" ;
                                   <http://tuc.web.engineering/module#hasCreditPoints>  "{modulePoints}" ;
                                   <http://across/university#hasUniversity>  <{universityUri}> ;
                                   <http://tuc/course#hasCourse>  <{courseUri}> . }}
        """
    return query


delete_module = "INSERT DATA { <%s>  <http://tuc.web.engineering/module#hasModules>  <%s> }"


def add_individual_module_by_admin(module_uuid_str, module_name, formatted_module_number, module_content, module_credit_points, university_uri, course_uri):
    query = f"""
    INSERT DATA {{
    <http://tuc.web.engineering/module#{module_uuid_str}> rdf:type <http://tuc.web.engineering/module#> .
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://tuc.web.engineering/module#hasModuleNumber> "{formatted_module_number}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://tuc.web.engineering/module#hasName> "{module_name}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://tuc.web.engineering/module#hasContent> "{module_content}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://tuc.web.engineering/module#hasCreditPoints> "{module_credit_points}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://across/university#hasUniversity> <{university_uri}>.
    <http://tuc.web.engineering/module#{module_uuid_str}> <http://tuc/course#hasCourse> <{course_uri}> .
    }}
    """

    return query

def get_course_uri_by_course_and_university_name(course_name, university_name):
    query = f"""
    SELECT ?courseUri
        WHERE {{
            ?course rdf:type <http://tuc/course#> .
            ?course <http://across/university#belongsToUniversity> ?university .
            ?university rdf:type <http://across/university#> .
            ?university <http://across/university#hasUniversityName> ?universityName .
            ?course <http://tuc/course#hasCourseName> ?courseName .
            
            BIND(str(?course) AS ?courseUri)

            FILTER (
                ?courseName = "{course_name}"^^<http://www.w3.org/2001/XMLSchema#string> &&
                ?universityName = "{university_name}"^^<http://www.w3.org/2001/XMLSchema#string>
            )
        }}
    """
    return query

def get_university_uri_by_university_name(university_name):
    query = f"""
    SELECT ?universityUri 
        WHERE {{
            ?university rdf:type <http://across/university#> .
            ?university <http://across/university#hasUniversityName> ?universityName .
            
            BIND(str(?university) AS ?universityUri)

            FILTER (
                ?universityName = "{university_name}"^^<http://www.w3.org/2001/XMLSchema#string>
            )
        }}
    """
    return query

def is_module_already_present(module_name, module_number, university_uri, course_uri):
    query = f"""
    ASK {{
    ?module rdf:type <http://tuc.web.engineering/module#> .
    ?module <http://tuc.web.engineering/module#hasName> "{module_name}"^^<http://www.w3.org/2001/XMLSchema#string> .
    ?module <http://tuc.web.engineering/module#hasModuleNumber> "{module_number}"^^<http://www.w3.org/2001/XMLSchema#string> .
    ?module <http://across/university#hasUniversity> <{university_uri}> .
    ?module <http://tuc/course#hasCourse> <{course_uri}> .
    }}
    """

    return query

def is_module_already_present_by_module_uri(module_uri):
    query = f"""
    ASK {{
    <{module_uri}> rdf:type <http://tuc.web.engineering/module#> .
    }}
    """

    return query

def delete_individual_module(module_uri):
    query = f"""
    DELETE WHERE {{
    <{module_uri}> ?predicate ?object .
    }}
    """

    return query  


def update_individual_module_by_admin(module_uri, updated_module_name, updated_module_number, updated_module_content, updated_module_credit_points, university_uri, course_uri):
    query = f"""
    DELETE {{
    <{module_uri}> <http://tuc.web.engineering/module#hasModuleNumber> ?oldModuleNumber .
    <{module_uri}> <http://tuc.web.engineering/module#hasName> ?oldName .
    <{module_uri}> <http://tuc.web.engineering/module#hasContent> ?oldContent.
    <{module_uri}> <http://tuc.web.engineering/module#hasCreditPoints> ?oldCreditPoints .
    
    }}
    INSERT {{
    <{module_uri}> <http://tuc.web.engineering/module#hasModuleNumber> "{updated_module_number}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <{module_uri}> <http://tuc.web.engineering/module#hasName> "{updated_module_name}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <{module_uri}> <http://tuc.web.engineering/module#hasContent> "{updated_module_content}"^^<http://www.w3.org/2001/XMLSchema#string> .
    <{module_uri}> <http://tuc.web.engineering/module#hasCreditPoints> "{updated_module_credit_points}"^^<http://www.w3.org/2001/XMLSchema#string> .
    }}
    WHERE {{
    <{module_uri}> rdf:type <http://tuc.web.engineering/module#> .
    <{module_uri}> <http://across/university#hasUniversity> <{university_uri}> .
    <{module_uri}> <http://tuc/course#hasCourse> <{course_uri}> .
    OPTIONAL {{
    <{module_uri}> <http://tuc.web.engineering/module#hasModuleNumber> ?oldModuleNumber .
    <{module_uri}> <http://tuc.web.engineering/module#hasName> ?oldName .
    <{module_uri}> <http://tuc.web.engineering/module#hasContent> ?oldContent.
    <{module_uri}> <http://tuc.web.engineering/module#hasCreditPoints> ?oldCreditPoints .
    }}
    }}
    """

    return query

def get_all_departments():
    query = f"""
    SELECT ?department (SAMPLE(?course) AS ?sampleCourse)
    WHERE {{
    ?course rdf:type <http://tuc/course#> .
    ?course <http://tuc/course#belongsToDepartment> ?department .
    }}
    GROUP BY ?department
    """
    return query