from firebase_admin import messaging, initialize_app, credentials
from django.conf import settings
import os

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "study-zed-notifications-firebase.json")

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_app = initialize_app(cred)

def  send_firebase_notification(registration_id, title, body, extra_data=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=registration_id,
        data=extra_data if extra_data else {}
    )

    try:
        response = messaging.send(message)
        return True, response
    except Exception as e:
        return False, str(e)