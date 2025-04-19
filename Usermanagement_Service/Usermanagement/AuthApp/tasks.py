from celery import shared_task
from AuthApp.services.email_service import EmailService

@shared_task(name="AuthApp.tasks.send_verification_email")
def send_verification_email(recipient_email):
    """Task to send verification email"""
    context = {
        "subject": "Email Verification - Study-Zed",
        "header": "Verify Your Email Address",
        "initial_otp": "Your OTP code",
    }
    
    result = EmailService.send_template_email(
        recipient=recipient_email,
        template_name="otp",
        context=context
    )
    
    return {
        "message": "Email verification process started",
        "task": result,
        "success": result["success"],
    }

@shared_task(name="AuthApp.tasks.resend_otp_verification_email")
def resend_otp_verification_email(recipient_email):
    """Task to resend verification OTP"""
    context = {
        "subject": "RESEND OTP for Verification - Study-Zed",
        "header": "Resend OTP to Verify Email",
        "initial_otp": "Your new OTP code",
    }
    
    result = EmailService.send_template_email(
        recipient=recipient_email,
        template_name="otp",
        context=context
    )
    
    return {
        "message": "Resend OTP verification process started",
        "task": result,
        "success": result["success"],
    }

@shared_task(name="AuthApp.tasks.send_password_reset_email")
def send_password_reset_email(recipient_email):
    """Task to send password reset email"""
    context = {
        "subject": "Password Reset - Study-Zed",
        "header": "Reset Your Password",
    }
    
    result = EmailService.send_template_email(
        recipient=recipient_email,
        template_name="forgot_password",
        context=context
    )
    
    return {
        "message": "Password reset email sent",
        "task": result,
        "success": result["success"],
    }