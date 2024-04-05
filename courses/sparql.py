def get_course_from_university_query(universityUri, universityName):
    query = f"""
        SELECT ?courseName ?courseUri ?courseNumber
        WHERE {{
            ?course rdf:type <http://tuc/course#> .
            ?course <http://across/university#belongsToUniversity> ?university .
            ?university rdf:type <http://across/university#> .
            ?university <http://across/university#hasUniversityName> ?universityName .
            ?course <http://tuc/course#hasCourseName> ?courseName .
            ?course <http://tuc/course#hasCourseNumber> ?courseNumber .
            
            BIND(str(?course) AS ?courseUri)
            BIND(str(?university) AS ?universityUri)

            FILTER (
                ?universityUri = "{universityUri}" &&
                ?universityName = "{universityName}"^^<http://www.w3.org/2001/XMLSchema#string>
            )
        }}
        ORDER BY ?courseName
        """
    return query
