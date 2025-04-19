import random
import string
import datetime
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Connect to Redis
redis_client = redis.StrictRedis(
    host=str(settings.REDIS_HOST), port=settings.REDIS_PORT, db=0, decode_responses=True
)

class OTPService:
    @staticmethod
    def generate_otp(email, length=6, expiry_minutes=10):
        """
        Generate a new OTP, store it in Redis, and return OTP with timestamps
        
        Args:
            email: User's email address
            length: Length of the OTP (default: 6)
            expiry_minutes: OTP validity period in minutes (default: 10)
            
        Returns:
            Tuple of (otp, created_at, expires_at)
        """
        try:
            # Generate a random OTP
            otp = ''.join(random.choices(string.digits, k=length))
            
            # Calculate timestamps
            created_at = datetime.datetime.now()
            expires_at = created_at + datetime.timedelta(minutes=expiry_minutes)
            
            # Store in Redis
            redis_client.hmset(email, {
                'otp': otp,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'is_authenticated': False,
                'no_of_try': 0,
                'resend_count': 0
            })
            
            # Set expiry in Redis
            redis_client.expire(email, expiry_minutes * 60)
            
            return otp, created_at, expires_at
            
        except Exception as e:
            logger.error(f"OTP generation error: {e}", exc_info=True)
            return None, None, None
    
    @staticmethod
    def verify_otp(email, otp):
        """
        Verify the OTP for the given email
        
        Args:
            email: User's email address
            otp: OTP to verify
            
        Returns:
            Boolean indicating whether OTP is valid
        """
        try:
            # Get OTP data from Redis
            otp_data = redis_client.hgetall(email)
            
            if not otp_data or 'otp' not in otp_data:
                return False, "OTP not found or expired"
                
            # Increment try count
            redis_client.hincrby(email, "no_of_try", 1)
            
            # Check try count
            try_count = int(otp_data.get('no_of_try', 0))
            if try_count >= 5:
                return False, "Maximum attempts exceeded"
                
            # Verify OTP
            if otp != otp_data['otp']:
                return False, "Invalid OTP"
                
            # Check expiry
            expires_at = datetime.datetime.fromisoformat(otp_data['expires_at'])
            if datetime.datetime.now() > expires_at:
                redis_client.delete(email)
                return False, "OTP has expired"
                
            # Mark as authenticated
            redis_client.hset(email, "is_authenticated", "True")
            
            return True, "OTP verified successfully"
            
        except Exception as e:
            logger.error(f"OTP verification error: {e}", exc_info=True)
            return False, f"Verification error: {str(e)}"