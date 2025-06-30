import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from django.conf import settings
from celery import shared_task
from django.core.mail import send_mail
from .tasks import generate_otp

logger = logging.getLogger(__name__)


def send_email_template(recipient, template_name, email_data):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD
    OTP, created_at, expires_at = generate_otp(email=recipient)
    email_data["otp"] = OTP

    try:
        template_path = os.path.join(
            settings.BASE_DIR, "templates", f"{template_name}.html"
        )
        with open(template_path, "r") as file:
            template_str = file.read()
        jinja_template = Template(template_str)
        email_content = jinja_template.render(email_data)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = email_data["subject"]
        msg.attach(MIMEText(email_content, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()

        return {
            "success": True,
            "message": "Email sent successfully",
            "otp": OTP,
            "created_at": created_at,
            "expires_at": expires_at,
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}


def send_direct_email(recipient, email_data):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD

    OTP, created_at, expires_at = generate_otp(email=recipient)
    try:
        send_mail(
            subject=email_data["subject"],
            message=(
                f"Dear user Your new OTP for password reset is:"
                + f"{OTP}  Thank You for being part of Sports_Maxx"
            ),
            from_email=sender_email,
            recipient_list=[recipient],
            fail_silently=True,
        )
        return {
            "success": True,
            "message": "Email sent successfully",
            "otp": OTP,
            "created_at": created_at,
            "expires_at": expires_at,
        }
    except Exception as e:
        logger.error(f"EMAIL UTIL Error details: {e}")

