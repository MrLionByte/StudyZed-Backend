from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
# from templated_email import send_templated_mail
import datetime
from django.utils.timezone import now
from datetime import timedelta
import random
import logging


def send_verification_email(recipient_list):
    OTP, created_at, expires_at = generate_OTP()
    subject = "Study-Zed Verify Email Address"
    body = f"Verify your email address pls Write the following code {OTP}"
    
    try :
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_list],
        )
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

def generate_OTP():
    otp = random.randint(100000, 999999)
    created_at = now() 
    expirired_at = created_at + timedelta(minutes=3)
    return otp, created_at, expirired_at 

def send_email(recipient_list):
    OTP, created_at, expires_at = generate_OTP()
    subject = "Study-Zed Verify Email Address"
    body = f"Verify your email address pls Write the following code {OTP}"