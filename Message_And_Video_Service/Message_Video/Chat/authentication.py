import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from asgiref.sync import sync_to_async
import os
import logging
from .jwt_decode import decode_jwt_token_for_chat
from .utils import get_user_by_id


logger = logging.getLogger(__name__)
SECRET_KEY = settings.JWT_SECRET_KEY


class JWTAuthentication:
    @sync_to_async
    def authenticate_websocket(self, token):
        try:
            user_data = decode_jwt_token_for_chat(token)
            user_id = user_data.get("user_id")
            if not user_id:
                logger.error("Invalid token payload: user_id not found.")
                raise PermissionDenied("Invalid token payload")

            # user = get_user_by_id(user_id)

            return user_data
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            raise PermissionDenied("Token has expired")

        except InvalidTokenError:
            logger.error("Invalid token.")
            raise PermissionDenied("Invalid token")

        except Exception as e:
            logger.error(f"Token decoding failed: {str(e)}")


# JWT Authentication for API requests
