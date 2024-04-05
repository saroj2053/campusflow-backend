from rdflib import Graph, Literal, RDF, URIRef
from sparql import *

graph = Graph()
graph.parse("./RDF_DATA/tuc_web_Engineering.rdf")
module_list = graph.query(module_list_query)
for module in module_list:
    uriUniversity = URIRef("http://across/university#TUC")
    uriCourse = URIRef("http://tuc/course#WebEngineering")
    graph.update(insert_module_univeristy  % (module.module,uriUniversity))
    graph.update(insert_module_course  % (module.module,uriCourse))


fileOneContent = graph.serialize(format='xml')
file1 = open('tuc_Web_Engineering.rdf', 'w')
file1.write(fileOneContent)
file1.close()