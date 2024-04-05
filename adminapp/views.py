import csv
from django.shortcuts import render

import os, json , os.path
from pymantic import sparql
from .sparql import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.core.files.storage import FileSystemStorage
from .universitiy_list import get_all_universities
from transfer_credits.models import TransferCredits
from .add_module import add_module_in_blaze
from django.http import HttpResponse
from user.models import UserProfile, UserData
from csv_to_rdf.csvTordf import University,CsvToRDF, UpdateModules, InsertModules
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from transfer_credits.views import send_generated_pdf_on_email
import requests
import uuid
from django.utils import timezone

EMAIL_BODY_APPROVED = """Hi {0}, 

Please find attached your transfer credit requests PDF. Your request has been approved.

Best regards,
CampusFlow Team"""

PDF_BODY_APPROVED = """Dear {0},

Your credit transfer request has been approved. Below is the list of transfer credit requests you made,

"""

SUBJECT_SUCCESSFUL = """Approved Credit Transfer"""

EMAIL_BODY_REJECTED = """Hi {0}, 

Please find attached your transfer credit requests PDF. Your request has been declined.

Best regards,
CampusFlow Team"""

PDF_BODY_REJECTED = """Dear {0},

Your credit transfer request has been declined. Below is the list of transfer credit requests you made,

"""

SUBJECT = """Credit Transfer"""

EMAIL_BODY = """Hi {0}, 

Please find attached your transfer credit requests PDF.

Best regards,
CampusFlow Team"""

PDF_BODY = """Dear {0},

Below is the list of transfer credit requests you made,

"""

SUBJECT_REJECTED = """Declined Credit Transfer"""

uploadLoaction =""
def saveFiles(uploaded_files):
    # Specify the directory where you want to save the files
    upload_directory = 'Backend/across/uploads/'

    # Create a FileSystemStorage instance with the upload directory
    fs = FileSystemStorage(location=upload_directory)
    uploadLoaction= fs.location
    print(fs.location)
    # Process and save the uploaded files
    saved_files = []
    for file in uploaded_files:
        saved_file = fs.save(file.name, file)
        saved_files.append(saved_file)
    return saved_files

@csrf_exempt
@require_POST
def csv_rdf(request):
    try:
       saved_files= saveFiles(request)  
       uni = University()
       unis = uni.get_all_university()
       csv_rdf= CsvToRDF(uni)
       csv_readers=[]

       for csvFile in saved_files:
                print(uploadLoaction)
                #replace the file path from csvfile
                file_path = r'C:\Users\User\Desktop\Source\web-wizards-11\uploads\Data2.csv'
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        csv_readers.append(row)
                csvModels=csv_rdf.get_all_csv_models(csv_readers, unis)
                csv_rdf.csvModules= csvModels
                upModule = UpdateModules()
                upModule.getUpdateModels(csv_rdf)
                inModule = InsertModules()
                inModule.insertModul(csv_rdf)
                return JsonResponse({'message': 'csv Files successfully converted to RDF file'}, status=200)
    except Exception as e:
            return JsonResponse({'message': f'Error converting csv to RDF file: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def clean_up_upload_folder(request):
    try:
        filelist = [ f for f in os.listdir("uploads/") if f.endswith(".rdf") ]
        for f in filelist:
         os.remove(os.path.join("uploads/", f))

        return JsonResponse({'message': 'Files deleted successfully'}, status=200)
    except Exception as e:
         return JsonResponse({'message': f'Error deleting files: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
def upload_file(request):
    try:
            uploaded_files = request.FILES.getlist('files')
            saved_files=saveFiles(uploaded_files)
        
            return JsonResponse({'message': 'Files uploaded and saved successfully', 'saved_files': saved_files}, status=200)
    except Exception as e:
            return JsonResponse({'message': f'Error uploading and saving files: {str(e)}'}, status=500)

    
@csrf_exempt
@require_GET
def get_universities(request):
    data = get_all_universities(request)
    return JsonResponse(data , safe=False)

def get_namespaces(graph):
    namespaces = {}
    for prefix, uri in graph.namespaces():
        namespaces[prefix] = Namespace(uri)
    return namespaces

@csrf_exempt
@require_POST
def insert_module(request):

    data = json.loads(request.body.decode('utf-8'))
    
    # Extract data fields
    email=data.get('email', '').strip()
    university_name= data.get('university','').strip()
    course_name = data.get('course','').strip()
    module_number = data.get('module_number','').strip()
    module_name = data.get('module_name','').strip()
    module_content = data.get('module_content','').strip()
    module_credit_points = data.get('module_credit_points','').strip()

    # Generate a UUID based on the current timestamp and node (hardware address)
    module_uuid = uuid.uuid1()

    # Convert the UUID to a string
    module_uuid_str = str(module_uuid)

    try:
        existing_user_profile = UserProfile.objects.filter(email=email).first()
        if existing_user_profile:
            if existing_user_profile.role == 'ADMIN':
                server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

                qresponse = server.query(get_university_uri_by_university_name(university_name))
                data_for_university_uri = qresponse['results']['bindings'] 
                for result in data_for_university_uri:
                    university_uri = str(result['universityUri']['value'])
                
                query = get_course_uri_by_course_and_university_name(course_name, university_name)
                qresponse = server.query(query)
                data_for_course_uri = qresponse['results']['bindings'] 
                for result in data_for_course_uri:
                    course_uri = str(result['courseUri']['value'])

                qresponse = server.query(is_module_already_present(module_name, module_number, university_uri, course_uri))
                
                # Module already exists, return a message
                if qresponse.get('boolean') is True:                    
                    response_data = {
                        'message': "Module already exists for the given University and Course.",
                        'module_name': module_name 
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    try:
                        payload = {'update': add_individual_module_by_admin(module_uuid_str, module_name, module_number, module_content, module_credit_points, university_uri, course_uri)}
        
                        result = requests.post("http://16.171.152.55/blazegraph/namespace/kb/sparql", data=payload)

                        # Check the response status
                        if result.status_code == 200:
                            response_data = {
                                'message': "Module Insertion successful.",
                                'module_name': module_name ,
                                'module_uri': f"http://tuc.web.engineering/module#{module_uuid_str}"
                            }
                            return JsonResponse(response_data, status=200)
                        
                    except Exception as ex:
                        # Handle other exceptions if needed
                        response_data = {
                                    'message': f"Module Insertion Failed - {str(ex)}" 
                        }
                        return JsonResponse(response_data, status =500)
            else:
                response_data = {
                    'message': "User doesn't have admin privileges!" 
                }
                return JsonResponse(response_data, status =403)
        else:
            response_data = {
                    'message': "User does not exist" 
            }
            return JsonResponse(response_data, status =404) 
    except Exception as ex:
        # Handle other exceptions if needed
        response_data = {
                    'message': f"Module Insertion Failed - {str(ex)}" 
        }
        return JsonResponse(response_data, status =500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_module(request):
    data = json.loads(request.body.decode('utf-8'))
    
    # Extract data fields
    email=data.get('email', '').strip()
    module_uri = data.get('module_uri','').strip()

    try:
        existing_user_profile = UserProfile.objects.filter(email=email).first()
        if existing_user_profile:
            if existing_user_profile.role == 'ADMIN':
                try:
                    server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')
                    qresponse = server.query(is_module_already_present_by_module_uri(module_uri))
                
                    # Module already exists, return a message
                    if qresponse.get('boolean') is False:                    
                        response_data = {
                            'message': "Module doesn't exist",
                            'module_uri': module_uri 
                        }
                        return JsonResponse(response_data, status=404)

                    payload = {'update': delete_individual_module(module_uri)}

                    result = requests.post("http://16.171.152.55/blazegraph/namespace/kb/sparql", data=payload)

                    # Check the response status
                    if result.status_code == 200:
                        response_data = {
                            'message': "Module deletion successful.",
                        }
                        return JsonResponse(response_data, status=200)
                        
                except Exception as ex:
                    # Handle other exceptions if needed
                    response_data = {
                                'message': f"Module Deletion Failed - {str(ex)}" 
                    }
                    return JsonResponse(response_data, status =500)
            else:
                response_data = {
                    'message': "User doesn't have admin privileges!" 
                }
                return JsonResponse(response_data, status =403)
        else:
            response_data = {
                    'message': "User does not exist" 
            }
            return JsonResponse(response_data, status =404) 
    except Exception as ex:
        # Handle other exceptions if needed
        response_data = {
                    'message': f"Module Deletion Failed - {str(ex)}" 
        }
        return JsonResponse(response_data, status =500)
    

@csrf_exempt
@require_http_methods(["PUT"])
def update_module(request):

    data = json.loads(request.body.decode('utf-8'))
    
    # Extract data fields
    email=data.get('email', '').strip()
    university_name= data.get('university','').strip()
    course_name = data.get('course','').strip()
    updated_module_number = data.get('module_number','').strip()
    updated_module_name = data.get('module_name','').strip()
    updated_module_content = data.get('module_content','').strip()
    updated_module_credit_points = data.get('module_credit_points','').strip()
    module_uri = data.get('module_uri','').strip()

    try:
        existing_user_profile = UserProfile.objects.filter(email=email).first()
        if existing_user_profile:
            if existing_user_profile.role == 'ADMIN':
                server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

                qresponse = server.query(is_module_already_present_by_module_uri(module_uri))
            
                # Module already exists, return a message
                if qresponse.get('boolean') is False:                    
                    response_data = {
                        'message': "Module doesn't exist, Please create module before updating",
                        'module_uri': module_uri 
                    }
                    return JsonResponse(response_data, status=404)

                qresponse = server.query(get_university_uri_by_university_name(university_name))
                data_for_unviersity_uri = qresponse['results']['bindings'] 
                for result in data_for_unviersity_uri:
                    university_uri = str(result['universityUri']['value'])
                
                query = get_course_uri_by_course_and_university_name(course_name, university_name)
                qresponse = server.query(query)
                data_for_course_uri = qresponse['results']['bindings'] 
                for result in data_for_course_uri:
                    course_uri = str(result['courseUri']['value'])
                try:
                    payload = {'update': update_individual_module_by_admin(module_uri, updated_module_name, updated_module_number, updated_module_content, updated_module_credit_points, university_uri, course_uri)}

                    result = requests.post("http://16.171.152.55/blazegraph/namespace/kb/sparql", data=payload)

                    # Check the response status
                    if result.status_code == 200:
                        response_data = {
                            'message': "Module Updation successful.",
                            'module_name': updated_module_name
                        }
                        return JsonResponse(response_data, status=200)           
                except Exception as ex:
                    # Handle other exceptions if needed
                    response_data = {
                                'message': f"Module Updation Failed - {str(ex)}" 
                    }
                    return JsonResponse(response_data, status =500)
            else:
                response_data = {
                    'message': "User doesn't have admin privileges!" 
                }
                return JsonResponse(response_data, status =403)
        else:
            response_data = {
                    'message': "User does not exist" 
            }
            return JsonResponse(response_data, status =404) 
    except Exception as ex:
        # Handle other exceptions if needed
        response_data = {
                    'message': f"Module Updation Failed - {str(ex)}" 
        }
        return JsonResponse(response_data, status =500)
    
@csrf_exempt
@require_POST
def fetch_transfer_credit_requests(request):
    data = json.loads(request.body.decode('utf-8'))

    # Extract data fields
    email=data.get('email', '').strip()

    try:
        list_of_transfer_credits = TransferCredits.objects.filter(email=email)
        transfer_credits_requests = []

        # Check if any objects are returned
        if list_of_transfer_credits.exists():
            # Access the objects in the queryset
            for transfer_credit in list_of_transfer_credits:
                transfer_credit_data = {
                    "fromModules": transfer_credit.fromModules,
                    "toModules": transfer_credit.toModules,
                    "created_at": transfer_credit.created_at,
                    "status": transfer_credit.status,
                    "updated_at": transfer_credit.updated_at,
                    "possibleTransferrableCredits": transfer_credit.possibleTransferrableCredits
                }
                transfer_credits_requests.append(transfer_credit_data)

        user_data = {  
            "transferCreditsRequests" : transfer_credits_requests
        }
        response= {
            'message': 'Successfully returned transfer credit requests of user',
            'user_data' : user_data
        }
        return JsonResponse(response, status =200)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)

@csrf_exempt
@require_http_methods("PUT")
def update_transfer_credit_request(request):

    data = json.loads(request.body.decode('utf-8'))

    try:
        # Extract data fields
        email=data.get('email', '').strip()
        updated_request=data.get('updatedRequest')
        list_of_transfer_credits = TransferCredits.objects.filter(email=email,fromModules=updated_request["fromModules"],toModules=updated_request["toModules"])
        updated_possibleTransferrableCredits = 0
        # Check if any objects are returned
        if list_of_transfer_credits.exists():
            # Access the objects in the queryset
            transfer_credits_requests = TransferCredits.objects.get(email=email,fromModules=updated_request["fromModules"],toModules=updated_request["toModules"])
            if transfer_credits_requests:
                current_credits = transfer_credits_requests.possibleTransferrableCredits
                subtracted_credits = int(transfer_credits_requests.toModules[0]['credits'])
                updated_possibleTransferrableCredits = current_credits - subtracted_credits       
                transfer_credits_requests.status = updated_request['status']
                transfer_credits_requests.possibleTransferrableCredits = updated_possibleTransferrableCredits
                transfer_credits_requests.updated_at = timezone.now()
                transfer_credits_requests.save()
            else:
                response_data = {
                    'message': "Transfer Credit Requests Updation Unsuccessful"
                }
                return JsonResponse(response_data, status =500) 

        # Retrieve all TransferCredit objects that match the filter criteria
        transfer_credits_list = TransferCredits.objects.filter(email = email)
        # Iterate through the queryset and update the 'possibleTransferrableCredits' field
        for updated_transfer_credits in transfer_credits_list:
            updated_transfer_credits.possibleTransferrableCredits = updated_possibleTransferrableCredits 
            updated_transfer_credits.save()
            
        user_profile = UserProfile.objects.get(email=email)
        if updated_request['status'] == "ACCEPTED":
            # Here Generating pdf and sending an email
            status_email = send_generated_pdf_on_email(data, user_profile, None,  EMAIL_BODY_APPROVED.format(user_profile.full_name), SUBJECT_SUCCESSFUL, PDF_BODY_APPROVED)
        else:
             status_email = send_generated_pdf_on_email(data, user_profile, None, EMAIL_BODY_REJECTED.format(user_profile.full_name), SUBJECT_REJECTED, PDF_BODY_REJECTED)
        response_data = {
                'message': "Transfer Credit Requests Updated Successfully"
        }
        return JsonResponse(response_data, status =200) 
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)
    
@csrf_exempt
@require_http_methods("PUT")
def send_email_transfer_credit(request):

    data = json.loads(request.body.decode('utf-8'))

    try:
        # Extract data fields
        email=data.get('email', '').strip()
        user_profile = UserProfile.objects.get(email=email)
        status_email = send_generated_pdf_on_email(data, user_profile, None, EMAIL_BODY.format(user_profile.full_name), SUBJECT, PDF_BODY)

        response_data = {
                'message': "Transfer Credit Requests sent Successfully"
        }
        return JsonResponse(response_data, status =200) 
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)

@csrf_exempt
@require_GET
def fetch_user_data(request):
    try:
        # Retrieve all entries of UserData
        user_data = UserData.objects.all()
        all_user_data = []
        # Convert the queryset to a list of dictionaries
        for entry in user_data:
            user_profile = UserProfile.objects.get(email=entry.email.email)        
            
            user_data_list = {'email': user_profile.email,
                               'full_name': user_profile.full_name,
                               'university': user_profile.university_name,
                               'role': user_profile.role}
            all_user_data.append(user_data_list)
        # Return the data as JSON response
        return JsonResponse({'user_data': all_user_data}, safe=False)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)
    
@csrf_exempt
@require_GET
def fetch_departments(request):
    server = sparql.SPARQLServer('http://16.171.152.55/bigdata/sparql')

    qresponse = server.query(get_all_departments())
    data_list = []
    data = qresponse['results']['bindings']
    
    for row in data:
        data_dict = {
            'department': str(row['department']['value'])
        }
        data_list.append(data_dict)
    return JsonResponse(data_list , safe=False)