import rdflib
import json

graph = rdflib.Graph()
graph.parse("data_all_possible.rdf")
query = f"""
        SELECT ?module ?moduleNumber ?moduleName ?moduleContent
        WHERE {{       
                    ?module <http://tuc.web.engineering/module#hasName> ?moduleName ;
                            <http://tuc.web.engineering/module#hasModuleNumber> ?moduleNumber ;
                            <http://tuc.web.engineering/module#hasContent> ?moduleContent .
        }}
    """
qresponse = graph.query(query)
data_list = []
for row in qresponse:
 data_dict = {
 'uri': str(row.module),
 'id': str(row.moduleNumber),
 'name': str(row.moduleName),
 'content': str(row.moduleContent),
 }
 data_list.append(data_dict)

print("Number of modules:", len(data_list))
json_data = json.dumps(data_list, indent=2)

with open('data_all_json.json', 'w', encoding='utf-8') as bialystok_modules_file:
    bialystok_modules_file.write(json_data)
bialystok_modules_file.close()