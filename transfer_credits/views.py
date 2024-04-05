import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from user.models import UserData, UserProfile
from .models import TransferCredits
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import ssl
import os
from reportlab.lib.units import inch, cm
from reportlab.platypus import Image

EMAIL_BODY_REQUEST = """Hi {0}, 

Please find attached your transfer credit requests PDF. You'll soon get contacted by our team on further updates.

Best regards,
CampusFlow Team"""

PDF_BODY_REQUEST = """Dear {0},

Your credit transfer request has been received and is currently being processed. We appreciate your patience during this time.

Below is the list of transfer credit requests you made, please check it once.

"""

SUBJECT = """Successful Credit Transfer Request"""

@csrf_exempt
@require_POST
def save_transferred_credits_by_user(request):
     # Get the raw request body
    body = request.body.decode('utf-8')
    try:
        # Parse JSON data from the request body
        data = json.loads(body)
        email = data.get('email','')
        signature = data.get('signature', '')
        transferCreditsRequest = data.get('transferCreditsRequest','')
        possibleTransferrableCredits = data.get('possibleTransferrableCredits','')
        user_profile = UserProfile.objects.get(email=email)
        try:
            for item in transferCreditsRequest:
                status = item['status']
                from_modules = item['fromModule']
                to_modules = item['toModule']
                created_at = item['createdAt']

                # Here it is checking does the same entry already exist or not, by checking email, fromModules and toModules
                list_of_transfer_credits = TransferCredits.objects.filter(email=email,fromModules=from_modules,toModules=to_modules)
                if not list_of_transfer_credits.exists():
                    # For Create again save() not required
                    transfer_credits = TransferCredits.objects.create(
                        email = email,
                        status = status,
                        fromModules = from_modules,
                        toModules = to_modules,
                        created_at = created_at
                        )
            
            # Retrieve all TransferCredit objects that match the filter criteria
            transfer_credits_list = TransferCredits.objects.filter(email = email)
            # Iterate through the queryset and update the 'possibleTransferrableCredits' field
            for updated_transfer_credits in transfer_credits_list:
                updated_transfer_credits.possibleTransferrableCredits = possibleTransferrableCredits 
                updated_transfer_credits.save()

            user_profile = UserProfile.objects.get(email=email)
           
            body = EMAIL_BODY_REQUEST.format(user_profile.full_name)

            # Here Generating pdf and sending an email
            status_email = send_generated_pdf_on_email(data, user_profile, signature, body, SUBJECT, PDF_BODY_REQUEST)
            
            if status_email is True:
                response = {
                    'message': 'PDF has been sent to your Email address, successfully requested for credit transfer'
                }
                return JsonResponse(response, status =200)
            else:
                response = {
                    'message': 'Issue during sending email'
                }
                return JsonResponse(response, status =500)
        except UserData.DoesNotExist:
            response = {
                'message': f'User data not found for the specified email:- {email}. Check if you marked your completed modules in your profile section first'
            }
            return JsonResponse(response, status=404)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)


@csrf_exempt
@require_POST
def fetch_transfer_credits_requests_by_user(request):

    body = request.body.decode('utf-8')

    try:
        # Parse JSON data from the request body
        data = json.loads(body)
        email = data.get('email','')
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
        
        except UserData.DoesNotExist:
            # Handle the case where UserData does not exist for the given email
            response = {
                'message': f'Transfer Requests not found for the given email: {email}',
                'user_data': {}
            }
            return JsonResponse(response, status=404)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)
 
def generate_pdf_for_user_email(data, user, signature, pdfBody):
    
    try:

        formatted_user_name = user.full_name.replace(' ','_')
        print("USER IS ",formatted_user_name)
        pdf_filename = f"Transfer_Requests_{formatted_user_name}.pdf"

        # Folder path to store the PDF file
        output_folder = "Transfer_Credit_Requests_Users_PDFs"

        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # PDF filename
        pdf_filename = os.path.join(output_folder, pdf_filename)
        # Create a PDF document
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)

        # Add content to the PDF
        styles = getSampleStyleSheet()
        style_center = ParagraphStyle('Center', parent=styles['Heading1'], alignment=TA_CENTER)
        elements = []

        # Heading of the PDF
        heading = Paragraph("CampusFlow Credit Transfer Requests", getSampleStyleSheet()["Title"])
        elements.append(heading)

        # Text before the table
        text_data_before = pdfBody.format(user.full_name)

        # Split the text into paragraphs based on line breaks
        text_paragraphs_before = text_data_before.split("\n")

        # Create a list of Paragraph objects
        new_paragraphs_before = [Paragraph(line, getSampleStyleSheet()["BodyText"]) for line in text_paragraphs_before]

        elements.extend(new_paragraphs_before)
        # # image = open(f"Backend/across/uploads/signature.png", "rb")  
        
        # Add a table for the data
        table_data = [["Status", "From Module", "To Module"]]


        if "transferCreditsRequest" in data:
            for item in data.get("transferCreditsRequest"):
                status = item.get("status", "")
                print("Status is : ", status)
                from_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in item.get("fromModule", [])])
                to_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in item.get("toModule", [])])
                table_data.append([status, from_module, to_module])
        elif "updatedRequest" in data:
            updatedRequest = data.get("updatedRequest")
            status = updatedRequest.get("status")
            from_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in updatedRequest.get("fromModules", [])])
            to_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in updatedRequest.get("toModules", [])])
            table_data.append([status, from_module, to_module])
        elif "sendEmailRequest" in data:
            for item in data.get("sendEmailRequest"):
                    status = item['status']
                    from_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in item.get("fromModule", [])])
                    to_module = ", ".join([f"{module['moduleName']} ({module['credits']} credits)" for module in item.get("toModule", [])])
                    table_data.append([status, from_module, to_module])                    

        # Define table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        # Create table
        table = Table(table_data)
        table.setStyle(table_style)
        elements.append(table)
        text_data_after = f"""
            <b>Total Possible Credits Transfer Requested: {data.get('possibleTransferrableCredits')} </b>

            If you have any further questions or concerns, please feel free to reach out to our support team.

            Thank you,
            CampusFlow Team
            """

        if "updatedRequest" in data or "sendEmailRequest" in data:
            # Text after the table
            text_data_after = f"""

            If you have any further questions or concerns, please feel free to reach out to our support team.

            Thank you,
            CampusFlow Team
            """

        text_paragraphs_after = text_data_after.split("\n")

        # Create a list of Paragraph objects
        new_paragraphs_after = [Paragraph(line, getSampleStyleSheet()["BodyText"]) for line in text_paragraphs_after]

        # Create a separate Paragraph for the bold line
        bold_line = Paragraph(new_paragraphs_after[0].text, getSampleStyleSheet()["BodyText"])

        # Apply bold style
        bold_line.style = getSampleStyleSheet()["BodyText"]
        bold_line.style.fontName = "Helvetica-Bold"

        # Replace the original line with the bold line
        new_paragraphs_after[0] = bold_line
 
        
        elements.extend(new_paragraphs_after)
        if signature is not None:
            im = Image(signature, hAlign="LEFT")
            elements.append(im)

        
        # Build the PDF document
        pdf.build(elements, onFirstPage=lambda canvas, doc: custom_footer(canvas, doc, "*This pdf is generated by CampusFlow Team, No Signature Required & All Copyrights Reserved with Web Wizards"))

        print(f"PDF generated successfully: {pdf_filename}")
        return pdf_filename
    except Exception as e:
        print(e)
        response = {
        'message': f"An unexpected error occurred during pdf creation: {e}"
        }
        return JsonResponse(response, status=500)

def custom_footer(canvas, doc, text):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillGray(0.5)
    
    # Get the width of the text and the page width
    text_width = canvas.stringWidth(text, "Helvetica", 9)
    page_width, _ = letter
    
    # Draw the text at the bottom-right corner
    canvas.drawString(page_width - text_width - 10, 10, text)
    
    canvas.restoreState()


def send_generated_pdf_on_email(data, user, signature=None, body=None, Subject=None, pdfBody=None):
    try:
        # Sender and recipient email addresses
        sender_email = "webwizardsservices@gmail.com"
        recipient_email = user.email

        formatted_user_name = user.full_name.replace(' ','_')

        # Create a message object
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = Subject

        message.attach(MIMEText(body, "plain"))

        # Add the generated PDF as an attachment
        # Folder path where the file is stored
        file_name = f"Transfer_Requests_{formatted_user_name}.pdf"

        # Construct the full file path
        with open(generate_pdf_for_user_email(data, user, signature, pdfBody), "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=file_name)
            part["Content-Disposition"] = f'attachment; filename="{file_name}"'
            message.attach(part)

        # Connect to the SMTP server and send the email
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "webwizardsservices@gmail.com"
        smtp_password = "podqlgpmunmenqiu"
        simple_email_context = ssl.create_default_context()

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=simple_email_context)
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        return True
    except Exception as e:
        response = {
        'message': f"An unexpected error occurred during sending an email: {e}"
        }
        return JsonResponse(response, status=500)