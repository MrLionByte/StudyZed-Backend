import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from asgiref.sync import  sync_to_async
import os
from .jwt_decode import decode_jwt_token_for_chat
from .utils import get_user_by_id

SECRET_KEY = settings.JWT_SECRET_KEY

class JWTAuthentication:
    @sync_to_async
    def authenticate_websocket(self, token):
        try:
            user_data = decode_jwt_token_for_chat(token)
            print("USER IN JWT",user_data)
            user_id = user_data.get("user_id")
            if not user_id:
                raise PermissionDenied("Invalid token payload")

            # user = get_user_by_id(user_id)

            return user_data  
        except ExpiredSignatureError:
            raise PermissionDenied("Token has expired")
        
        except InvalidTokenError:
            raise PermissionDenied("Invalid token")
        
        except Exception as e:
            print("ERROR in JWT AUTHENTICATION", e)