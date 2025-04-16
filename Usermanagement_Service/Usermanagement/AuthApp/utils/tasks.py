import redis
import random
import string
from django.conf import settings
from datetime import datetime, timedelta
from celery import shared_task
from .utils.email_utils import send_email_template, send_direct_email

redis_client = redis.StrictRedis(
    host=str(settings.REDIS_HOST), port=settings.REDIS_PORT, db=0, decode_responses=True
)

@shared_task(name='auth.send_verification_email')
def send_verification_email(recipient_email):
    email_data = {
        'subject': 'Email Verification - Study-Zed',
        'header': 'Verify Your Email Address',
        'initial_otp': 'Your OTP code',
    }
    return send_email_template(recipient_email, 'otp', email_data)

@shared_task(name='auth.resend_otp_verification_email')
def resend_otp_verification_email(recipient_email):
    email_data = {
        'subject': 'Resend OTP for Verification - Study-Zed',
        'header': 'Resend OTP to Verify Email',
        'initial_otp': 'Your new OTP code',
    }
    return send_email_template(recipient_email, 'otp', email_data)

def generate_otp(email, length=6):
    print("GEN OTP EMAIL:", type(email))
    otp = "".join(random.choices(string.digits, k=length))
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=5)
    key = f"{email}"
    if redis_client.hgetall(key):
        redis_client.hmset(
            key,
            {
                "otp": otp,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
            },
        )

    else:
        redis_client.hmset(
            key,
            {
                "otp": otp,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "resend_count": 0,
                "no_of_try": 0,
                "is_authenticated": "False",
                "is_blocked": "False",
            },
        )
    redis_client.expire(key, 24 * 60 * 60)
    return otp, created_at, expires_at
