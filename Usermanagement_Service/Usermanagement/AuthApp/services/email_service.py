import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task
from .otp_service import OTPService

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_template_email(recipient, template_name, context=None):
        """Send email using a template"""
        try:
            otp, created_at, expires_at = OTPService.generate_otp(recipient)
            
            context = context or {}
            context["otp"] = otp
            
            template_path = os.path.join(
                settings.BASE_DIR, "templates", f"{template_name}.html"
            )
            with open(template_path, "r") as file:
                template_str = file.read()
            
            jinja_template = Template(template_str)
            email_content = jinja_template.render(context)
            
            sender_email = settings.EMAIL_HOST_USER
            
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = context.get("subject", "Notification")
            msg.attach(MIMEText(email_content, "html"))
            
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(sender_email, recipient, msg.as_string())
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "task": {
                    "otp": otp,
                    "created_at": created_at,
                    "expires_at": expires_at,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }
    
    @staticmethod
    def send_direct_email(recipient, subject, message):
        """Send plain text email"""
        try:
            otp, created_at, expires_at = OTPService.generate_otp(recipient)
            message = f"{message}\nYour OTP is: {otp}"
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "task": {
                    "otp": otp,
                    "created_at": created_at,
                    "expires_at": expires_at,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }