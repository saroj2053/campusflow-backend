from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD
from compare_modules.sparql import *
import os
from django.conf import settings


def add_predicate_for_module_similarity(universityOneModulesFile, univeristyTwoModulesFile, data_list_first, data_list_second, consumer):
    modulesTUC = Graph()
    modulesBialstok = Graph()
    modulesTUC.parse(universityOneModulesFile)
    modulesBialstok.parse(univeristyTwoModulesFile)
    consumer.send_message({"progress": 20 ,"type": 11 ,"message": "Starting to update RDF files:"})
    for similar_module in data_list_first:
       consumer.send_message({"progress": 30 , "type": 11, "message": f"Updating file"})
       list = similar_module['similar_modules']
       for item in list:
           uri = URIRef(item)
           modulesTUC.update(insert_module_similarity  % (similar_module.uri,uri))
           
    for similar_module in data_list_second:
       consumer.send_message({"progress": 40 ,"type": 11 ,"message": f"Updating file"})
       list = similar_module['similar_modules']
       for item in list:
           uri = URIRef(item)
           modulesBialstok.update(insert_module_similarity  % (similar_module.uri,uri))
    
    consumer.send_message({"progress": 50 ,"type": 11 , "message": "Finialising Results"})    
    fileOneContent = modulesTUC.serialize(format='xml')
    fileTwoContent = modulesBialstok.serialize(format='xml')

    # Extract the filename without the extension
    new_file_name_1 = universityOneModulesFile

    filename_without_extension = os.path.splitext(os.path.basename(univeristyTwoModulesFile))[0]
    new_file_name_2 = filename_without_extension + "_similar.rdf"

    file1 = open(new_file_name_1, 'w')
    # Define the folder name
    folder_name = os.path.join(settings.BASE_DIR, f'RDF//Similarity Data//')

    # Ensure the folder exists, create it if it doesn't
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Encode content to bytes using UTF-8
    fileOneContentBytes = fileOneContent.encode('utf-8')
    fileTwoContentBytes = fileTwoContent.encode('utf-8')

    consumer.send_message({"progress": 60 ,"type": 12 ,"message": "Almost Finished"})   

    # Construct the full file paths within the folder
    # new_file_path_1 = os.path.join(folder_name, new_file_name_1)
    new_file_path_2 = os.path.join(folder_name, new_file_name_2)

    # Open the files and write the content
    with open(new_file_name_1, 'wb') as file1:
        file1.write(fileOneContentBytes)

    with open(new_file_path_2, 'wb') as file2:
        file2.write(fileTwoContentBytes)

    consumer.send_message({"progress": 100 ,"type": 12 ,"message": f"Updating RDF files process finished successfully"})
    file1.close()
    file2.close()
