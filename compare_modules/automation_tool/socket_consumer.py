import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .module_similarity import read_modules_and_compare
from os import listdir
from os.path import isfile, join
import os
from compare_modules.sparql import * 
from pymantic import sparql
from django.conf import settings
from .course_similarity import find_similarity_between_courses
class Consumer(WebsocketConsumer):
    def connect(self):
        try:
            self.accept()
            self.send(text_data=json.dumps({"progress": 1 , "message": "Converstion Started"}))
            
        except Exception as e:
            print(f"Error in connection {str(e)}")

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)
        response_data = json.loads(text_data)
        print(response_data)
        if response_data['message'] == "start" :
            print("starting message")
            # Assuming your desired directory is two levels up from the current working directory
            
            # # Sample Data
            # response_data = {
            # 'message': "Data is Here",
            # 'university_name': "Bialystok University",
            # 'rdf_File_Path': "BU_Let'sseecourse2"
            # }

            # Construct the absolute path
            server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

            # # Getting University URI
            qresponse = server.query(get_other_universities_except_given(response_data['university_name']))
            data_for_university = qresponse['results']['bindings'] 
            # # Initialize an empty list to store university names
            university_names_list = []

            # file_path = f"RDF_DATA//{response_data['university_name']}//{response_data['rdf_File_Path'].lower()}.rdf"
            file1 = os.path.join(settings.BASE_DIR, 'RDF_DATA', f"{response_data['university_name']}", f"{response_data['rdf_File_Path'].lower()}.rdf")

            # # Iterate through the results and store university names in the list
            for result in data_for_university:
                university_name = str(result['universityName']['value'])
                university_names_list.append(university_name)


            folder_path = os.path.join(settings.BASE_DIR, 'RDF',  'Similarity Data')
            # Check if the folder exists, if not, create it
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # # Iterate through the list
            for university_name in university_names_list:
                absolute_path =os.path.join(settings.BASE_DIR, 'RDF_DATA', f'{university_name}')                            
                folder_path = absolute_path
                similar_courses_list = find_similarity_between_courses(response_data, university_name)
                
                # Filter out files that do not exist
                only_files_in_folder = [os.path.join(folder_path, filename) for filename in similar_courses_list if os.path.isfile(os.path.join(folder_path, filename))]
                read_modules_and_compare(file1, only_files_in_folder, self)
    
    def send_message(self, value):
        
        # message = event['message']

        self.send(text_data=json.dumps(value))