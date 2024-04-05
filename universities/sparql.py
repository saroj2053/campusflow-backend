university_list_query = """
SELECT ?universityName ?hasUniversityId ?university
WHERE {
    ?university <http://across/university#hasUniversityName> ?universityName ;
            <http://across/university#hasUniversityId> ?hasUniversityId .
}
"""
