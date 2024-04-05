from rdflib import Graph

graph = Graph()

graph.parse("data_merged.rdf")
graph.parse("data.rdf")

bialystok_modules_data = graph.serialize(format='xml')
with open('data_all_possible.rdf', 'w', encoding='utf-8') as bialystok_modules_file:
    bialystok_modules_file.write(bialystok_modules_data)
bialystok_modules_file.close()