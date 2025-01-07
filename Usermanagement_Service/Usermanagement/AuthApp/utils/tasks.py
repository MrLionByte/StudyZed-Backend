import redis
import random
import string
from datetime import datetime, timedelta

redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


def generate_otp(email, length=6):
    print("GEN OTP EMAIL:", type(email))
    otp = "".join(random.choices(string.digits, k=length))
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=5)
    key = f"{email}"
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
