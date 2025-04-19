import jwt
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def decode_jwt_token(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        secret_key = settings.JWT_SECRET_KEY
        decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        jwt_data = {
            "user_role": decoded_payload.get("role"),
            "user_code": decoded_payload.get("user_code"),
            "user_email": decoded_payload.get("email"),
            "user_id": decoded_payload.get("id"),
        }
        return jwt_data

    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token has expired: {e}")
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        logger.error(f"Invalid token: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 