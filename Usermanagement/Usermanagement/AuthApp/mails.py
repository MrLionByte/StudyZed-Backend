# # from .utils.email_utils import send_email_template
from .utils.email_utils import *
from celery import shared_task

# # Example: Send Verification Email
@shared_task
def send_verification_email(recipient_email):
    email_data = {
        "subject": "Email Verification - Study-Zed",
        "header": "Verify Your Email Address",
        "initial_otp": "Your OTP code",
    }
    print("  MAX  2  :", email_data)
    task = send_email_template(
        recipient=recipient_email,
        template_name="otp",
        email_data=email_data
    )
    print("TASK :", task)
    return {
        "message": "Email verification process started",
        'task': task,
        'success': True,
    }


def send_forgot_password_email(recipient_email):
    print(recipient_email)
    email_data = {
        "subject": "Password Reset - Study-Zed",
        "header": "Reset Your Password",
    }
    send = send_direct_email(
        recipient=recipient_email,
        # subject="Password Reset - Study-Zed",
        # template_name="forgot_password.html",
        email_data=email_data
    )
    print("SEND :", send)
    return send


# def resend_otp_verification_email(recipient_email):
#     email_data = {
#         "subject": "OTP resend for Email Verification - Study-Zed",
#         "header": "Verify Your Email Address",
#         "initial_otp": "Your Resend OTP code",
#     }
#     return send_email_template(
#         recipient_list=recipient_email,
#         subject=email_data["subject"],
#         template_name="otp",
#         email_data=email_data
#     )




# mails.py

# from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# import uuid
# from datetime import timedelta, datetime
