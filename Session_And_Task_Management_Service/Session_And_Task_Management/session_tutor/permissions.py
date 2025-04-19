from rest_framework import permissions, validators, status
import jwt
import logging
from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied, NotFound
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)

class TutorAccessPermission(permissions.BasePermission):
    message = 'Permission denied.'
    
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        secret_key = settings.JWT_SECRET_KEY
        
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            if decoded_payload.get("role") == "TUTOR":
                return True
            else:
                logger.error("Permission denied, not a tutor.")
                raise AuthenticationFailed("Permission denied, not a tutor.")
        
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired.")
            raise AuthenticationFailed("Token has expired.")
        
        except jwt.InvalidTokenError:
            logger.error("Invalid token.")
            raise AuthenticationFailed("Invalid token.")
        
        except Exception as e:
            logger.error(f"Token decoding failed: {str(e)}")
            raise AuthenticationFailed("Authentication failed.")
