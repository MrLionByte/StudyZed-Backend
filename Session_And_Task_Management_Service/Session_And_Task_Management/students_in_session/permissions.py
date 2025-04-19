from rest_framework import permissions, validators
import jwt
from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed
import logging
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

logger = logging.getLogger(__name__)

class StudentAccessPermission(permissions.BasePermission):
    message = 'Permission denied.'

    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        secret_key = settings.JWT_SECRET_KEY
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            if decoded_payload.get("role") == "STUDENT":
                return True
            else:
                logger.error("Permission denied, not a student.")
                raise AuthenticationFailed("Permission denied, not a student.")
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            self.message = "Token has expired."
            raise AuthenticationFailed(detail="Token has expired.", code=401)
        except InvalidTokenError:
            logger.error("Invalid token.")
            self.message = "Invalid token."
            raise AuthenticationFailed(detail="Invalid token.", code=401)
