import rdflib
from compare_modules.sparql import *
from .live_updates import send_updates
def readRDFFile(file):
 graph = rdflib.Graph()
 
 graph.parse(file)
 v = graph.serialize(format='xml')
 print("value:"+v)
 
 module_list = graph.query(module_list_query)
 module_first_only = graph.query(module_list_query_first_item_only)
 return module_list, module_first_only
 
