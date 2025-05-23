import jwt
from django.conf import settings
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from Chat.models import User
import logging

logger = logging.getLogger(__name__)

def decode_jwt_token(request):
    token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
    secret_key = settings.JWT_SECRET_KEY
    decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    jwt_data = {
        "user_role": decoded_payload.get("role"),
        "user_code": decoded_payload.get("user_code"),
        "user_email": decoded_payload.get("email"),
        "user_id": decoded_payload.get("user_id"),
    }

    if not User.objects(user_code=jwt_data["user_code"]).first():
        user = User(
            user_id=jwt_data["user_id"],
            user_code=jwt_data["user_code"],
            user_role=jwt_data["user_role"],
            email=jwt_data["user_email"],
        )
        user.save()
    return jwt_data


def decode_jwt_token_for_chat(token):
    try:
        secret_key = settings.JWT_SECRET_KEY
        decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        jwt_data = {
            "user_role": decoded_payload.get("role"),
            "user_code": decoded_payload.get("user_code"),
            "user_email": decoded_payload.get("email"),
            "user_id": decoded_payload.get("user_id"),
        }
        return jwt_data

    except ValidationError as e:
        logger.error("Validation error in JWT decode", e)
        raise AuthenticationFailed("Invalid token")

    except Exception as e:
        logger.error("Error decoding JWT token", e)
        raise AuthenticationFailed("Invalid token")
