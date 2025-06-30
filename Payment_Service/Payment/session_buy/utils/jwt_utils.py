import jwt
from django.conf import settings

def decode_jwt_token(request):
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

