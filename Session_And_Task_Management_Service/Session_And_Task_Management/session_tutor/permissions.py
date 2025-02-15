from rest_framework import permissions, validators, status
import jwt
from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class TutorAccessPermission(permissions.BasePermission):
    message = 'Permission denied.'
    
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        print("TOKEN IN permission TUT:",token)
        secret_key = settings.JWT_SECRET_KEY
        
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            if decoded_payload.get("role") == "TUTOR":
                print("TUTOR")
                return True
            else:
                print("NOT TUTOR")
                raise AuthenticationFailed("Permission denied, not a tutor.")
        except ExpiredSignatureError:
            print("Expired")
            self.message = "Token has expired."
            raise AuthenticationFailed(detail="Token has expired.", code=401)
        except InvalidTokenError:
            print("Signature Error")
            self.message = "Invalid token."
            raise AuthenticationFailed(detail="Invalid token.", code=401)
