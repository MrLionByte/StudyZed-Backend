# from django.core.mail import EmailMessage, send_mail
# from django.conf import settings
# from django.template.loader import render_to_string
# # from templated_email import send_templated_mail
# import datetime
# from django.utils.timezone import now
# from django.utils import timezone
# from datetime import timedelta
import random
import string

# # Python Email temp library : 
# # mail to celery



# def send_verification_email(recipient_list):
#     OTP, created_at, expires_at = generate_OTP()
#     subject = "Study-Zed Verify Email Address"
#     body = f"Verify your email address pls Write the following code {OTP}"
    
#     try :
#         send_mail(
#             subject=subject,
#             message=body,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[recipient_list],
#         )
#         print("  SUCCESS  ")
#         return {
#             "success": True,
#             "message": "Email sent successfully",
#             "otp": OTP,
#             "created_at": created_at,
#             "expires_at": expires_at,
#         }
        
#     except Exception as e:
#         print(f"Error details: {e}")
#         return {"success": False, "message": f"Failed to send email: {str(e)}"}

# def generate_OTP():
#     otp = random.randint(111110, 999999)
#     created_at = timezone.now()
#     expire_at =created_at+timedelta(minutes=3)
#     print(otp, created_at, expire_at, "  XXXX  ")
#     return otp, created_at, expire_at


from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from django.conf import settings
import os

# This will be a mock function for generating OTP
def generate_OTP():
    otp = random.randint(111110, 999999)
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=5)
    return otp, created_at, expires_at


# Forgot password OTP
def generate_forgot_otp(length=6):
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choice(characters, k=length))
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=3)
    return otp, created_at, expires_at


# Function to send verification email using SMTP and Jinja2
def send_verification_email(recipient_list):
    # Generate OTP and expiration time
    
    OTP, created_at, expires_at = generate_OTP()
    print(" WORKING 1111 ")
    # Define email server and credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "fanunaf25@gmail.com"
    sender_password = "nses jwwu fnya tbnl"
    print(" WORKING 1122 ")
    
    # Set up the Jinja2 template for the email
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'otp.html')
    with open(template_path, "r") as file:
        template_str = file.read()
        print(template_str)
    print(" WORKING 1133 ")
    jinja_template = Template(template_str)
    print("  WOKING 000 " ,jinja_template)
    # Define email content using Jinja2 template data
    email_data = {
        "subject": "Study-Zed Verify Email Address",
        "greeting": f"Hello !",
        "otp": OTP,
        "message": "Verify your email address by entering the following code.",
        "sender_name": "Study-Zed Team",
        "created_at": created_at,
        "expires_at": expires_at,
    }
    print(" WORKING 11444 ")
    # Render the HTML email content with dynamic data
    email_content = jinja_template.render(email_data)
    print(" WORKING 11555 ")
    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_list
    msg["Subject"] = email_data["subject"]
    print(" WORKING 11666 ")
    # Attach the rendered HTML content to the email
    msg.attach(MIMEText(email_content, "html"))
    print(" WORKING 11777 ")
    try:
        print( "  :::::  0011  ::::::")
        # Set up email server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        print( "  :::::  0022  ::::::")
        server.starttls()
        print( "  :::::  0033  ::::::")
        server.login(sender_email, sender_password)
        print(" WORKING 11988 ")
        # Send email
        server.sendmail(sender_email, recipient_list, msg.as_string())
        print(" WORKING 11999 ")
        # Close the server connection
        server.quit()

        print(f"Email successfully sent to {recipient_list}")

        return {
            "success": True,
            "message": "Email sent successfully",
            "otp": OTP,
            "created_at": created_at,
            "expires_at": expires_at,
        }

    except Exception as e:
        print(f"Error details: {e}")
        return {"success": False, "message": f"Failed to send email: {str(e)}"}



def send_mail_template():
    pass