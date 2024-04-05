module_list_query = """
SELECT ?moduleName ?moduleId ?moduleContent ?moduleURI ?module ?moduleCreditPoints ?moduleWorkLoad
WHERE {
    ?module <http://tuc.web.engineering/module#hasName> ?moduleName ;
            <http://tuc.web.engineering/module#hasModuleNumber> ?moduleId ;
            <http://tuc.web.engineering/module#hasContent> ?moduleContent ;
            <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints ;
            <http://tuc.web.engineering/module#hasWorkLoad> ?moduleWorkLoad
}
"""


module_list_query_first_item_only = """
SELECT ?moduleContent
WHERE {
    ?module <http://tuc.web.engineering/module#hasContent> ?moduleContent .
   
}
LIMIT 1
"""

insert_module_similarity = """INSERT {
    ?subject <http://tuc.web.engineering/module#hasModules> ?resource
}
WHERE {
  BIND(<%s> AS ?subject)
  BIND(<%s> AS ?resource)
}"""

insert_module_univeristy = "INSERT DATA { <%s>  <http://across/university#hasUniversity>  <%s> }"

insert_module_course = "INSERT DATA { <%s>  <http://tuc/course#hasCourse>  <%s> }"


def add_course(uuid_numeric_only, course_uri, course_name, belongs_to_program, belongs_to_department, university_uri,has_language):
    query = f"""
        INSERT DATA {{ 
            <{course_uri}> rdf:type <http://tuc/course#> ;
                    <http://tuc/course#hasCourseName> "{course_name}" ;
                    <http://tuc/course#hasCourseNumber> "{uuid_numeric_only}" ;
                    <http://tuc/course#belongsToProgram> "{belongs_to_program}" ;
                    <http://tuc/course#hasLanguage> "{has_language}" ;
                    <http://tuc/course#belongsToDepartment> "{belongs_to_department}" ;
                    <http://across/university#belongsToUniversity>  <{university_uri}> .
               }}
    """
    return query

def get_other_universities_except_given(university_name):
    query = f"""
        SELECT ?universityId ?universityName ?city ?country
        WHERE {{
        ?university rdf:type <http://across/university#> .
        ?university <http://across/university#hasUniversityId> ?universityId .
        ?university <http://across/university#hasUniversityName> ?universityName .
        ?university <http://across/university#isLocatedInCity> ?city .
        ?university <http://across/university#isLocatedInCountry> ?country .

        FILTER (?universityName != "{university_name}")
        }}
    """
    return query


def get_course_uri_from_departments_and_university(department, university, language, programType):
    query= f"""
    SELECT ?course ?universityName ?university ?hasLanguage
    WHERE {{
    ?course rdf:type <http://tuc/course#> .
    ?course <http://tuc/course#belongsToDepartment> "{department}" .
    ?course <http://tuc/course#belongsToProgram> "{programType}" .
    ?course <http://tuc/course#hasLanguage> ?hasLanguage .
    ?course <http://across/university#belongsToUniversity> ?university .
    ?university rdf:type <http://across/university#> .
    ?university <http://across/university#hasUniversityName> ?universityName .
      FILTER (
                ?universityName = "{university}"^^<http://www.w3.org/2001/XMLSchema#string> && 
        		?hasLanguage = "{language}"
            )
    }}

    """
    return query