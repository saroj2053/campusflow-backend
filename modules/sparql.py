list_with_similar_modules_query = """
SELECT ?module ?similarModule (SAMPLE(?moduleId) as ?sampleModuleId) (SAMPLE(?moduleName) as ?sampleModuleName) (SAMPLE(?moduleContent) as ?sampleModuleContent)(SAMPLE(?moduleCreditPoints) as ?sampleModuleCreditPoints) (SAMPLE(?universityName) as ?sampleUniversity) (SAMPLE(?courseName) as ?sampleCourse) (SAMPLE(?similarModuleId) as ?sampleSimilarModuleId)  (SAMPLE(?similarModuleName) as ?sampleSimilarModuleName) (SAMPLE(?similarModuleContent) as ?sampleSimilarModuleContent)(SAMPLE(?similarModuleCreditPoints) as ?sampleSimilarModuleCreditPoints) (SAMPLE(?universityNameSimilar) as ?sampleSimilarUnivserity) (SAMPLE(?courseNameSimilar) as ?sampleSimilarCourse)
        WHERE {{
            ?module <http://tuc.web.engineering/module#hasName> ?moduleName ;
                <http://tuc.web.engineering/module#hasModuleNumber> ?moduleId ;
                <http://tuc.web.engineering/module#hasContent> ?moduleContent ;
                <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints ;
                <http://tuc.web.engineering/module#hasModules> ?similarModule ;
                <http://across/university#hasUniversity> ?university ;
                <http://tuc/course#hasCourse> ?course .
            ?university <http://across/university#hasUniversityName> ?universityName .
            ?course <http://tuc/course#hasCourseName> ?courseName .
            ?similarModule <http://tuc.web.engineering/module#hasName> ?similarModuleName;
                        <http://tuc.web.engineering/module#hasModuleNumber> ?similarModuleId ;
                        <http://tuc.web.engineering/module#hasContent> ?similarModuleContent;
                        <http://tuc.web.engineering/module#hasCreditPoints> ?similarModuleCreditPoints ;
                        <http://across/university#hasUniversity> ?similarUniversity ;
                        <http://tuc/course#hasCourse> ?similarCourse .
            ?similarUniversity <http://across/university#hasUniversityName> ?universityNameSimilar .
            ?similarCourse <http://tuc/course#hasCourseName> ?courseNameSimilar .

        }}
GROUP BY ?module ?similarModule
"""

def get_similar_module_against_module_uri_query(moduleUri):
    list_all_against_uri_with_similar_modules_query = f"""
        SELECT ?module ?similarModuleWorkLoad ?similarMouleLanguage ?similarModuleProgram ?similarModuleDepartment ?moduleId ?moduleName ?moduleContent ?moduleCreditPoints ?universityName ?courseName ?similarModule ?similarModuleName ?similarModuleContent ?similarModuleCreditPoints ?similarModuleId ?universityNameSimilar ?courseNameSimilar
        WHERE {{
            ?module <http://tuc.web.engineering/module#hasName> ?moduleName ;
                <http://tuc.web.engineering/module#hasModuleNumber> ?moduleId ;
                <http://tuc.web.engineering/module#hasContent> ?moduleContent ;
                <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints ;
                <http://tuc.web.engineering/module#hasModules> ?similarModule ;
                <http://across/university#hasUniversity> ?university ;
                <http://tuc/course#hasCourse> ?course .
            ?university <http://across/university#hasUniversityName> ?universityName .
            ?course <http://tuc/course#hasCourseName> ?courseName .
            ?similarModule <http://tuc.web.engineering/module#hasName> ?similarModuleName;
                        <http://tuc.web.engineering/module#hasModuleNumber> ?similarModuleId ;
                        <http://tuc.web.engineering/module#hasContent> ?similarModuleContent;
                        <http://tuc.web.engineering/module#hasCreditPoints> ?similarModuleCreditPoints ;
                        <http://tuc.web.engineering/module#hasWorkLoad> ?similarModuleWorkLoad ;
                        <http://across/university#hasUniversity> ?similarUniversity ;
                        <http://tuc/course#hasCourse> ?similarCourse .
            ?similarUniversity <http://across/university#hasUniversityName> ?universityNameSimilar .
            ?similarCourse <http://tuc/course#hasCourseName> ?courseNameSimilar .
            ?similarCourse <http://tuc/course#belongsToProgram> ?similarModuleProgram .
            ?similarCourse <http://tuc/course#hasLanguage> ?similarMouleLanguage  .
            ?similarCourse <http://tuc/course#belongsToDepartment> ?similarModuleDepartment .

            BIND(str(?module) AS ?moduleUri)
            
            FILTER (
                    ?moduleUri = "{moduleUri}"
                    )
        }}
    """
    return list_all_against_uri_with_similar_modules_query

def get_modules_from_course_and_university_query(courseUri, courseName, universityUri):
    query = f"""
        SELECT ?moduleUri (SAMPLE (?moduleName) as ?sampleModuleName) (SAMPLE(?moduleNumber) as ?sampleModuleNumber) (SAMPLE(?moduleContent) as ?sampleModuleContent) (SAMPLE(?moduleCreditPoints) as ?sampleModuleCreditPoints)
        WHERE {{       
            ?module rdf:type <http://tuc.web.engineering/module#> .
            ?module <http://tuc.web.engineering/module#hasName> ?moduleName .
            ?module <http://tuc.web.engineering/module#hasModuleNumber> ?moduleNumber .
            ?module <http://tuc.web.engineering/module#hasContent> ?moduleContent .
            ?module <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints .
            ?course rdf:type <http://tuc/course#> .
            ?module <http://tuc/course#hasCourse> ?course .
          	?course <http://tuc/course#hasCourseName> ?courseName .
            ?university rdf:type <http://across/university#> .
            ?course <http://across/university#belongsToUniversity> ?university .  
          
          	BIND(str(?course) AS ?courseUri)
            BIND(str(?university) AS ?universityUri)
            BIND(str(?module) AS ?moduleUri)
            
            FILTER (
              (?courseUri = "{courseUri}" && ?courseName = "{courseName}"^^<http://www.w3.org/2001/XMLSchema#string>) &&
              ?universityUri = "{universityUri}"
            )
        }}
        GROUP BY ?moduleUri
        ORDER BY ?sampleModuleName
        """
    return query

def get_all_modules_query():
    query = f"""
         SELECT ?moduleUri  (SAMPLE(?courseBelongsToDepartment) as ?sampleModuleBelongsToDepartment) (SAMPLE(?courseHasLanguage) as ?sampleModuleHasLanguage) (SAMPLE(?courseProgram) as ?sampleModuleBelongsToProgram) (SAMPLE(?moduleWorkLoad) as ?sampleModuleWorkLoad) (SAMPLE(?moduleNumber) as ?sampleModuleNumber) (SAMPLE(?moduleName) as ?sampleModuleName) (SAMPLE(?moduleContent) as ?sampleModuleContent) (SAMPLE(?moduleCreditPoints) as ?sampleModuleCreditPoints) (SAMPLE(?universityName) as ?sampleUniversityName) (SAMPLE(?courseName) as ?sampleCourseName)
        WHERE {{       
                    ?module rdf:type <http://tuc.web.engineering/module#> .
                    ?module <http://tuc.web.engineering/module#hasName> ?moduleName .
                    ?module <http://tuc.web.engineering/module#hasModuleNumber> ?moduleNumber .
                    ?module <http://tuc.web.engineering/module#hasContent> ?moduleContent .
                    ?module <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints .
                    ?module <http://tuc.web.engineering/module#hasWorkLoad> ?moduleWorkLoad .
                    ?course rdf:type <http://tuc/course#> .
                    ?module <http://tuc/course#hasCourse> ?course .
                    ?course <http://tuc/course#hasCourseName> ?courseName .
                    ?course <http://tuc/course#belongsToProgram> ?courseProgram .
                    ?course <http://tuc/course#belongsToDepartment> ?courseBelongsToDepartment .
                    ?course <http://tuc/course#hasLanguage> ?courseHasLanguage .
                    ?university rdf:type <http://across/university#> .
                    ?course <http://across/university#belongsToUniversity> ?university .  
                    ?university <http://across/university#hasUniversityName> ?universityName .

                    BIND(str(?module) AS ?moduleUri)
        }}
        GROUP BY ?moduleUri
    """
    return query


def get_module_details_from_module_uri(moduleUri):
    query = f"""
        SELECT ?module ?moduleId ?moduleName ?moduleContent ?moduleCreditPoints ?universityName ?courseName ?similarModule
        WHERE {{
            ?module <http://tuc.web.engineering/module#hasName> ?moduleName ;
                <http://tuc.web.engineering/module#hasModuleNumber> ?moduleId ;
                <http://tuc.web.engineering/module#hasContent> ?moduleContent ;
                <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints ;
                <http://across/university#hasUniversity> ?university ;
                <http://tuc/course#hasCourse> ?course .

            BIND(str(?module) AS ?moduleUri)
            
            OPTIONAL {{
        		?module <http://tuc.web.engineering/module#hasSimilarModule> ?similarModule .
    		}}
            
            FILTER (
                    ?moduleUri = "{moduleUri}"
            )
        }}
    """
    return query



def get_searched_modules_query(search_term):
    query= f"""
        SELECT ?moduleUri  (SAMPLE(?courseBelongsToDepartment) as ?sampleModuleBelongsToDepartment) (SAMPLE(?courseHasLanguage) as ?sampleModuleHasLanguage) (SAMPLE(?courseProgram) as ?sampleModuleBelongsToProgram) (SAMPLE(?moduleWorkLoad) as ?sampleModuleWorkLoad) (SAMPLE(?moduleNumber) as ?sampleModuleNumber) (SAMPLE(?moduleName) as ?sampleModuleName) (SAMPLE(?moduleContent) as ?sampleModuleContent) (SAMPLE(?moduleCreditPoints) as ?sampleModuleCreditPoints) (SAMPLE(?universityName) as ?sampleUniversityName) (SAMPLE(?courseName) as ?sampleCourseName)
        WHERE {{       
                    ?module rdf:type <http://tuc.web.engineering/module#> .
                    ?module <http://tuc.web.engineering/module#hasName> ?moduleName .
                    ?module <http://tuc.web.engineering/module#hasModuleNumber> ?moduleNumber .
                    ?module <http://tuc.web.engineering/module#hasContent> ?moduleContent .
                    ?module <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints .
                    ?module <http://tuc.web.engineering/module#hasWorkLoad> ?moduleWorkLoad .
                    ?course rdf:type <http://tuc/course#> .
                    ?module <http://tuc/course#hasCourse> ?course .
                    ?course <http://tuc/course#hasCourseName> ?courseName .
                    ?course <http://tuc/course#belongsToProgram> ?courseProgram .
                    ?course <http://tuc/course#belongsToDepartment> ?courseBelongsToDepartment .
                    ?course <http://tuc/course#hasLanguage> ?courseHasLanguage .
                    ?university rdf:type <http://across/university#> .
                    ?course <http://across/university#belongsToUniversity> ?university .  
                    ?university <http://across/university#hasUniversityName> ?universityName .

                    BIND(str(?module) AS ?moduleUri)
                    FILTER (
                        regex(?moduleName, "{search_term}", "i")
                    )
        }}
        GROUP BY ?moduleUri
        """
    return query


def get_module_details_query(moduleUri):
    query = f"""
        SELECT ?moduleUri  ?courseBelongsToDepartment ?courseHasLanguage ?courseProgram ?moduleWorkLoad ?moduleNumber ?moduleName ?moduleCreditPoints ?universityName ?courseName ?moduleContent
        WHERE {{       
                    ?module rdf:type <http://tuc.web.engineering/module#> .
                    ?module <http://tuc.web.engineering/module#hasName> ?moduleName .
                    ?module <http://tuc.web.engineering/module#hasModuleNumber> ?moduleNumber .
                    ?module <http://tuc.web.engineering/module#hasContent> ?moduleContent .
                    ?module <http://tuc.web.engineering/module#hasCreditPoints> ?moduleCreditPoints .
                    ?module <http://tuc.web.engineering/module#hasWorkLoad> ?moduleWorkLoad .
                    ?course rdf:type <http://tuc/course#> .
                    ?module <http://tuc/course#hasCourse> ?course .
                    ?course <http://tuc/course#hasCourseName> ?courseName .
                    ?course <http://tuc/course#belongsToProgram> ?courseProgram .
                    ?course <http://tuc/course#belongsToDepartment> ?courseBelongsToDepartment .
                    ?course <http://tuc/course#hasLanguage> ?courseHasLanguage .
                    ?university rdf:type <http://across/university#> .
                    ?course <http://across/university#belongsToUniversity> ?university .  
                    ?university <http://across/university#hasUniversityName> ?universityName .

            BIND(str(?module) AS ?moduleUri)
            
            OPTIONAL {{
        		?module <http://tuc.web.engineering/module#hasSimilarModule> ?similarModule .
    		}}
            
            FILTER (
                    ?moduleUri = "{moduleUri}"
            )
        }}
    """
    return query