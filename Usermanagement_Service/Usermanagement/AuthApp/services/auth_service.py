import time
import logging
from django.utils import timezone
from zoneinfo import ZoneInfo
from celery.result import AsyncResult
from AuthApp.models import Email_temporary, UserAddon
from AuthApp.utils.auth_helpers import reset_login_count
from .email_service import EmailService
from .otp_service import OTPService

logger = logging.getLogger(__name__)

class AuthenticationService:
    @staticmethod
    def start_email_verification(email):
        """
        Initiates the email verification process by sending a verification email
        and creating a temporary email entry.
        """
        try:
            # Check if email exists in temp storage and delete if found
            temp_data = Email_temporary.objects.filter(email=email).first()
            if temp_data:
                temp_data.delete()
                logger.info(f"Deleted existing temporary email record for {email}")
            
            # Send verification email
            email_result = EmailService.send_template_email(
                recipient=email,
                template_name="verification_email",
                context={"subject": "Email Verification"}
            )
            
            if not email_result["success"]:
                logger.error(f"Failed to send verification email to {email}")
                return False, None
            
            # Create temporary email record
            otp = email_result["task"]["otp"]
            expires_at = timezone.make_aware(
                email_result["task"]["expires_at"], timezone=ZoneInfo("UTC")
            )
            
            Email_temporary.objects.create(
                email=email, 
                otp=otp,
                expires_at=expires_at
            )
            
            return True, email_result
                
        except Exception as e:
            logger.error(f"Email verification error: {e}", exc_info=True)
            return False, {"error": str(e)}
    
    @staticmethod
    def resend_verification_email(email):
        """
        Resends the verification email and updates the temporary email record.
        """
        try:
            # Delete existing temporary email entry if any
            temp_data = Email_temporary.objects.filter(email=email).first()
            if temp_data:
                temp_data.delete()
            
            # Send new verification email
            email_result = EmailService.send_template_email(
                recipient=email,
                template_name="verification_email",
                context={"subject": "Email Verification (Resend)"}
            )
            
            if not email_result["success"]:
                return False, None
            
            # Create new temporary email record
            otp = email_result["task"]["otp"]
            expires_at = timezone.make_aware(
                email_result["task"]["expires_at"], timezone=ZoneInfo("UTC")
            )
            
            Email_temporary.objects.create(
                email=email, 
                otp=otp,
                expires_at=expires_at
            )
            
            return True, email_result
                
        except Exception as e:
            logger.error(f"Resend verification error: {e}", exc_info=True)
            return False, {"error": str(e)}
    
    @staticmethod
    def verify_otp(email, otp):
        """
        Verifies the OTP for the given email.
        """
        try:
            user_under_verification = Email_temporary.objects.get(email=email)
            
            # Increment try count
            user_under_verification.no_of_try += 1
            user_under_verification.save()
            
            # Check maximum attempts
            if user_under_verification.no_of_try > 5:
                return False, "Maximum tries exceeded"
            
            # Verify OTP
            if user_under_verification.otp != otp:
                return False, "Invalid OTP"
            
            # Check expiry
            current_time = timezone.now()
            if current_time > user_under_verification.expires_at:
                user_under_verification.delete()
                return False, "OTP has expired"
            
            # Mark as authenticated
            user_under_verification.is_authenticated = True
            user_under_verification.save()
            return True, "OTP verified successfully"
            
        except Email_temporary.DoesNotExist:
            return False, "Email verification record not found"
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password
        """
        try:
            user = UserAddon.objects.get(email=email)
            
            if not user.check_password(password):
                return None, "Invalid password"
            
            if not user.is_active:
                return None, "User account is blocked"
            
            reset_login_count(email)
            return user, "Authentication successful"
            
        except UserAddon.DoesNotExist:
            return None, "User does not exist"
    
    @staticmethod
    def send_forgot_password_email(email):
        """
        Send a forgot password email with OTP
        """
        try:
            user = UserAddon.objects.get(email=email)
            
            if not user.is_active:
                return False, "User account is blocked"
            
            email_result = EmailService.send_template_email(
                recipient=email,
                template_name="forgot_password_email",
                context={"subject": "Password Reset"}
            )
            
            return True, email_result
            
        except UserAddon.DoesNotExist:
            return False, "User does not exist"