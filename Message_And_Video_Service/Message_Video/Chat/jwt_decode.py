import jwt
from django.conf import settings
from rest_framework.exceptions import ValidationError

def decode_jwt_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    secret_key = settings.JWT_SECRET_KEY
    decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    jwt_data = {
        "user_role": decoded_payload.get("role"),
        "user_code": decoded_payload.get("user_code"),
        "user_email": decoded_payload.get("email"),
        "user_id": decoded_payload.get("user_id"),
    }
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
        print("VALIDATION in JWT DECODE", e)
    
    except Exception as e:
        print("ERROR in JWT DECODE",e)