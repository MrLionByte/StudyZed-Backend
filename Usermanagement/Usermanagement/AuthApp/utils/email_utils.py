import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from datetime import datetime, timedelta
from django.conf import settings
import random
import string

def generate_OTP(length=6):
    otp = ''.join(random.choices(string.digits, k=length))
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=5)
    return otp, created_at, expires_at

def send_email_template(recipient_list, subject, template_name, email_data):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD
    
    OTP, created_at, expires_at = generate_OTP()
    print("OTP :",OTP, created_at, expires_at)
    email_data['otp'] = OTP
    
    try:
        template_path = os.path.join(settings.BASE_DIR, 'templates', f'{template_name}.html')
        with open(template_path, "r") as file:
            template_str = file.read()
        jinja_template = Template(template_str)
        email_content = jinja_template.render(email_data)
        
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_list
        msg["Subject"] = subject
        msg.attach(MIMEText(email_content, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_list, msg.as_string())
        server.quit()
        
        return {
            "success": True,
            "message": "Email sent successfully",
            "otp": OTP,
            "created_at": created_at,
            "expires_at": expires_at,
            }
    except Exception as e:
        print(f"EMAIL UTIL Error details: {e}")
        return {
            "success": False, 
            "message": f"Failed to send email: {str(e)}"
                }