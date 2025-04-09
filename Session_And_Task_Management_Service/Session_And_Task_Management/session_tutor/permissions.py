from rest_framework import permissions, validators, status
import jwt
from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied, NotFound
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework.response import Response
from django.conf import settings

class TutorAccessPermission(permissions.BasePermission):
    message = 'Permission denied.'
    
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        secret_key = settings.JWT_SECRET_KEY
        
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            if decoded_payload.get("role") == "TUTOR":
                print("TUTOR")
                return True
            else:
                print("NOT TUTOR")
                raise AuthenticationFailed("Permission denied, not a tutor.")
        
        except jwt.ExpiredSignatureError:
           
            print("Error XZ: Signature has expired")
            raise AuthenticationFailed("Token has expired.")
        
        except jwt.InvalidTokenError:
            
            print("Error XX: Invalid token")
            raise AuthenticationFailed("Invalid token.")
        
        except Exception as e:
            
            print("Error XY:", e)
            raise AuthenticationFailed("Authentication failed.")
