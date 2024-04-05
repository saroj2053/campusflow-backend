def get_all_courses():
    query = f"""
    SELECT ?course ?courseNumber ?courseName ?program ?language ?department
    WHERE {{
    ?course rdf:type <http://tuc/course#> .
    ?course <http://tuc/course#hasCourseNumber> ?courseNumber .
    ?course <http://tuc/course#hasCourseName> ?courseName .
    ?course <http://tuc/course#belongsToProgram> ?program .
    ?course <http://tuc/course#hasLanguage> ?language .
    ?course <http://tuc/course#belongsToDepartment> ?department .
    }}   
    """
    return query
