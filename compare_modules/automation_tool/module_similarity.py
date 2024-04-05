from .upload_file_to_blazegraph import upload_file_to_blazegraph
from .translator import translateModules
from .update_rdf_module import add_predicate_for_module_similarity
import ssl
import spacy
from os import listdir
from os.path import isfile, join
import os
import shutil
from django.conf import settings
from .read_rdf_module_file import readRDFFile
from django.http import JsonResponse


def read_modules_and_compare(universityOneModulesFile, only_files_in_folder, consumer):
    try:
     _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
     pass
    else:
     ssl._create_default_https_context = _create_unverified_https_context
    nlp = spacy.load('en_core_web_lg')
    if len(only_files_in_folder) > 0:
        firstUniversityModules = translateModules(universityOneModulesFile, consumer)
        for file_name in only_files_in_folder:
            univeristyTwoModulesFile = file_name
            consumer.send_message({"progress": 2 , "type": 0 , "message": "Starting module conversions"})
            consumer.send_message({"progress": 3 , "type": 10, "message": "First modules file translated to english successfully"})
            secondUniversityModules = translateModules(univeristyTwoModulesFile , consumer)
            consumer.send_message({"progress": 4 , "type": 10, "message": "Second modules file translated to english successfully"})
            data_list_first = []
            data_list_second = []
            consumer.send_message( {"progress": 6 , "type": 10, "message": "Starting to find similarities between modules"})
            filteredFirstUniversityModules , filteredSecondUniversityModules = filter_modules_by_workload(firstUniversityModules, secondUniversityModules)
            count = 2
            for module in filteredFirstUniversityModules:
                for module2 in filteredSecondUniversityModules:
                    text1 = module.name if(module.moduleContent == "This course has not yet been described...") else module.moduleContent
                    text2 = module2.name if(module2.moduleContent == "This course has not yet been described...") else module2.moduleContent
                    similarity = find_text_similarity_spacy(text1, text2, nlp)
                    consumer.send_message({"progress": 5 * count , "type": 2 if similarity else 3, "message": f"{module.name} - {module2.name} are similar : {similarity}"})
                    if(similarity):
                        similar_modules_m1 = []
                        similar_modules_m2 = []
                        similar_modules_m1.append(module2.uri)
                        similar_modules_m2.append(module.uri)
                        module['similar_modules'] = similar_modules_m1
                        module2['similar_modules'] = similar_modules_m2
                        data_list_first.append(module)
                        data_list_second.append(module2)
                        consumer.send_message({"progress": 50 , "type": 10, "message": "Starting to find similarities between modules"})
                count = count + 0.1    
                
            add_predicate_for_module_similarity(universityOneModulesFile, univeristyTwoModulesFile, data_list_first, data_list_second, consumer)
    else:
        consumer.send_message({"progress": 100 , "type": 12, "message": "No Comparable Modules found"})      
    # Moving New hasModules file to Similarity Folder
    source_path = universityOneModulesFile
    filename_without_extension = os.path.splitext(os.path.basename(source_path))[0]
    new_filename = filename_without_extension
    ## NEED TO CHANGE THIS ACCORDING TO REQUIREMENT
    destination_folder =os.path.join(settings.BASE_DIR, 'RDF', 'Similarity Data')
    new_file_path_destination_file = os.path.join(settings.BASE_DIR, 'RDF', 'Similarity Data' , f'{new_filename}_similar.rdf')
    shutil.copy(source_path, new_file_path_destination_file)
    upload_file_to_blazegraph(destination_folder, "", False)
    
    return {}
    

def find_text_similarity_spacy(module1Content, module2Content, nlp):
    
    s1 = nlp(module1Content)
    s2 = nlp(module2Content)
    
    s1_verbs = " ".join([token.lemma_ for token in s1 if token.pos_ == "VERB"])
    s1_adjs = " ".join([token.lemma_ for token in s1 if token.pos_ == "ADJ"])
    s1_nouns = " ".join([token.lemma_ for token in s1 if token.pos_ == "NOUN"])

    s2_verbs = " ".join([token.lemma_ for token in s2 if token.pos_ == "VERB"])
    s2_adjs = " ".join([token.lemma_ for token in s2 if token.pos_ == "ADJ"])
    s2_nouns = " ".join([token.lemma_ for token in s2 if token.pos_ == "NOUN"])
    
    verbs_similarity = nlp(s1_verbs).similarity(nlp(s2_verbs))
    adj_similarity = nlp(s1_adjs).similarity(nlp(s2_adjs))
    noun_similarity = nlp(s1_nouns).similarity(nlp(s2_nouns))
    
    is_similar = True if(verbs_similarity >= 0.8 and adj_similarity >= 0.8 and noun_similarity >= 0.9) else False
    return is_similar

def filter_modules_by_workload(firstUniversityModules, secondUniversityModules):
    try:
        secondUniModulesSet = set()
        secondUniModules = []
        firstUniModules = []
        for firstModule in firstUniversityModules:
            flag = False  
            for secondModule in secondUniversityModules:
                # Taking out difference between module credit points as a last alternative of comparison
                difference_between_credits = abs(int(firstModule.moduleCreditPoints) - int(secondModule.moduleCreditPoints))
                # EUROPEAN UNION FIGURES CALCULATION
                minWorkLoad = 25 * int(secondModule.moduleCreditPoints)
                maxWorkLoad = 30 * int(secondModule.moduleCreditPoints)
                # Here we are checking if given module workload is already more or equal than
                # other university module workload then add that module directly
                if(int(firstModule.moduleWorkLoad) >= int(secondModule.moduleWorkLoad)):
                    secondUniModules.append(secondModule)
                    flag = True
                elif((int(firstModule.moduleWorkLoad) < int(secondModule.moduleWorkLoad)) and difference_between_credits <= 2):
                   # Here we are checking if given module workload is less than 
                   # other university module workload then check according  
                   # to european union is it under conditions if yes then add that module
                   # else leave that module(it might have certain different requirements)
                   if (minWorkLoad <= int(secondModule.moduleWorkLoad) <= maxWorkLoad): 
                        secondUniModules.append(secondModule)
                        flag = True

            # If secondModule adding then respective firstModule should get added
            if(flag == True):
                firstUniModules.append(firstModule)
        secondUniModulesSet = set(secondUniModules)
        filteredSecondModulesList = list(secondUniModulesSet)
        return firstUniModules, filteredSecondModulesList
    except Exception as e:
        return JsonResponse({'message': f'Error during finding similarities between courses: {str(e)}'}, status=500)    