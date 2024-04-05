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