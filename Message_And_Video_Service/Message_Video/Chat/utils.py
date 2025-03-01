import base64
import json
import os
import requests
from rest_framework.exceptions import PermissionDenied
from .custom_user import CustomUser

USER_SERVICE_URL = "http://127.0.0.1:8005/class-app/tutor-session-details/"


def decode_jwt(token):
    """Decodes the JWT and returns the payload."""
    parts = token.split('.')
    if len(parts) != 3:
        return None

    payload_base64 = parts[1]
    
    padding = len(payload_base64) % 4
    if padding:
        payload_base64 += '=' * (4 - padding)
        
    payload_json = base64.urlsafe_b64decode(payload_base64)
    payload = json.loads(payload_json)
    return payload

def get_user_by_id(user_id):
    try:
        url = f"{USER_SERVICE_URL}/?{tutor_code}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            return CustomUser(user_data)
        else:
            raise PermissionDenied("User not found in user service or invalid ID")
    except requests.exceptions.RequestException as e:
        raise PermissionDenied(f"Error occurred while fetching user: {str(e)}")