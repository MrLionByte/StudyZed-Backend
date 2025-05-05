import jwt
import logging
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from asgiref.sync import  sync_to_async
import os
from Chat.jwt_decode import decode_jwt_token_for_chat

SECRET_KEY = settings.JWT_SECRET_KEY
logger = logging.getLogger(__name__)

class JWTAuthentication:
    @sync_to_async
    def authenticate_websocket(self, token):
        try:
            user_data = decode_jwt_token_for_chat(token)
            user_id = user_data.get("user_id")
            if not user_id:
                raise PermissionDenied("Invalid token payload")

            return user_data  
        except ExpiredSignatureError:
            raise PermissionDenied("Token has expired")
        
        except InvalidTokenError:
            raise PermissionDenied("Invalid token")
        
        except Exception as e:
            logger.error("ERROR in JWT AUTHENTICATION", str*(e))