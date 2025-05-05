# # from .utils.email_utils import send_email_template
from .utils.email_utils import send_email_template, send_direct_email, send_mail
from celery import shared_task


@shared_task(name="AuthApp.mails.send_verification_email")
def send_verification_email(recipient_email):
    email_data = {
        "subject": "Email Verification - Study-Zed",
        "header": "Verify Your Email Address",
        "initial_otp": "Your OTP code",
    }
    task = send_email_template(
        recipient=recipient_email, template_name="otp", email_data=email_data
    )
    return {
        "message": "Email verification process started",
        "task": task,
        "success": True,
    }


def send_forgot_password_email(recipient_email):
    email_data = {
        "subject": "Password Reset - Study-Zed",
        "header": "Reset Your Password",
    }
    send = send_direct_email(
        recipient=recipient_email,
        # subject="Password Reset - Study-Zed",
        # template_name="forgot_password.html",
        email_data=email_data,
    )
    return send


@shared_task(name="AuthApp.mails.resend_otp_verification_email")
def resend_otp_verification_email(recipient_email):
    email_data = {
        "subject": "RESEND OTP for Verification - Study-Zed",
        "header": "REsend OTP to Verify Email",
        "initial_otp": "Your new OTP code",
    }
    task = send_email_template(
        recipient=recipient_email, template_name="otp", email_data=email_data
    )
    return {
        "message": "Resend OTP verification process started",
        "task": task,
        "success": True,
    }
    return send_email_template(
        recipient_list=recipient_email,
        subject=email_data["subject"],
        template_name="otp",
        email_data=email_data
    )


# mails.py

# from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# import uuid
# from datetime import timedelta, datetime
