from django.utils import timezone
from zoneinfo import ZoneInfo
from celery.result import AsyncResult
from AuthApp.models import Email_temporary, UserAddon
from AuthApp.mails import send_verification_email, resend_otp_verification_email
from AuthApp.utils.auth_helpers import reset_login_count

class AuthenticationService:
    @staticmethod
    def start_email_verification(email):
        """
        Initiates the email verification process by creating a temporary email entry.
        """
        try:
            email_task = send_verification_email.apply_async(args=[email])
            result = AsyncResult(email_task.id)
            
            for _ in range(10):
                if result.status == "SUCCESS":
                    data = result.get(timeout=3)
                    expires_at = timezone.make_aware(
                        data["task"]["expires_at"], timezone=ZoneInfo("UTC")
                    )
                    Email_temporary.objects.create(
                        email=email, otp=data["task"]["otp"], expires_at=expires_at
                    )
                    return True, data
                time.sleep(1)    
            return False, None
        
        except Exception as e:
            return False
        
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
        """Authenticate user with email and password"""
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