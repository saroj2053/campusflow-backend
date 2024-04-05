from django.urls import path
from .views import csv_rdf, upload_file, update_module, delete_module, insert_module, get_universities, fetch_transfer_credit_requests, update_transfer_credit_request, fetch_user_data, clean_up_upload_folder, fetch_departments, send_email_transfer_credit
from pdf_To_rdf.views import pdfToRdf

urlpatterns= [
    path('pdfToRdf', pdfToRdf, name='pdf-rdf'),
    path('upload', upload_file, name='upload-file'),
    path('universitieslist', get_universities, name="get-universities"),
    path('insertModule', insert_module, name='insert-module'),
    path('deleteModule', delete_module, name='delete-module'),
    path('updateModule', update_module, name='update-module'),
    path('fetchTransferCreditRequests', fetch_transfer_credit_requests, name='fetch-transfer-credit-requests'),
    path('updateTransferRequest', update_transfer_credit_request, name='update-transfer-credit-request'),
    path('sendEmailTransferRequest', send_email_transfer_credit, name='send_email_transfer_credit'),
    path('fetchUserData', fetch_user_data, name='fetch-user-data'),
    path('deleteclean', clean_up_upload_folder, name='clean_directory'),
    path('fetchDepartments', fetch_departments, name='fetch_departments'),

]