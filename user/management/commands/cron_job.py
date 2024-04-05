import schedule
import time
from django.core.management.base import BaseCommand
from transfer_credits.models import TransferCredits
from user.models import UserProfile
from datetime import datetime, timedelta
from tzlocal import get_localzone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import ssl
from django.http import JsonResponse
from transfer_credits.views import generate_pdf_for_user_email


def check_status_job():
    print("I'm working...")
    transferCreditsRequest = []
    possibleTransferrableCredits = 0
    transfer_request_for_pending = TransferCredits.objects.filter(status = "PENDING")
    if transfer_request_for_pending.exists():
        for pending_requests in transfer_request_for_pending:
            transfer_requests_user = transfer_request_for_pending.filter(email = pending_requests.email)
            transferCreditsRequest = []
            for individual_requests in transfer_requests_user:
                try:
                    local_timezone = get_localzone()
                    created_at_time = individual_requests.created_at.astimezone(local_timezone)
                except Exception as e:
                    # Handle the case where the timezone is unknown
                    created_at_time = individual_requests.created_at

                current_time = datetime.now(local_timezone) 
                # Perform the subtraction
                difference = current_time - created_at_time

                if difference > timedelta(minutes=1):
                    data = {
                        "fromModule": [
                            {
                                "moduleUri": individual_requests.fromModules[0]['moduleUri'],
                                "moduleName": individual_requests.fromModules[0]['moduleName'],
                                "moduleId": individual_requests.fromModules[0]['moduleId'],
                                "credits": individual_requests.fromModules[0]['credits']
                            }
                        ],
                        "toModule": [
                            {
                                "moduleUri": individual_requests.toModules[0]['moduleUri'],
                                "moduleName": individual_requests.toModules[0]['moduleName'],
                                "moduleId": individual_requests.toModules[0]['moduleId'],
                                "credits": individual_requests.toModules[0]['credits']
                            }
                        ],
                        "status": individual_requests.status,
                    }
                    transferCreditsRequest.append(data)
                    possibleTransferrableCredits = individual_requests.possibleTransferrableCredits
            requests = {
                "transferCreditsRequest": transferCreditsRequest,
                "possibleTransferrableCredits": possibleTransferrableCredits
            }
            print(requests)
            user_profile = UserProfile.objects.get(email= individual_requests.email)
            send_generated_pdf_on_email_cron_job(requests, user_profile)
                            
PDF_BODY_REQUEST = """Dear {0},

I hope this message finds you well. We would like to remind you about the pending credit transfer requests that are awaiting your attention. Your timely review and approval are crucial to ensure a smooth processing flow.

Below is the list of transfer credit requests that require your prompt review:
"""

def send_generated_pdf_on_email_cron_job(data, user):
    try:
        # Sender and recipient email addresses
        sender_email = "webwizardsservices@gmail.com"
        recipient_email = user.email
        print(recipient_email)
        formatted_user_name = user.full_name.replace(' ','_')

        # Create a message object
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Gentle Reminder: Credit Transfer Request"

        # Add body text
        body = f"""Hi {user.full_name}, 

Please find attached your transfer credit requests PDF. You'll soon get contacted by our team on further updates.

Best regards,
CampusFlow Team"""
        message.attach(MIMEText(body, "plain"))

        # Add the generated PDF as an attachment
        # Folder path where the file is stored
        file_name = f"Transfer_Requests_{formatted_user_name}.pdf"

        # Construct the full file path
        with open(generate_pdf_for_user_email(data, user, None, PDF_BODY_REQUEST), "rb") as attachment:
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
            print("SUCCESS........")
        return True
    except Exception as e:
        response = {
        'message': f"An unexpected error occurred during sending an email: {e}"
        }
        return JsonResponse(response, status=500)


class Command(BaseCommand):
    help = 'Runs a job every 10 seconds'

    def handle(self, *args, **options):
        # Schedule the job every 30 seconds
        schedule.every(10).minutes.do(check_status_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
