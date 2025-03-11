from firebase_admin import messaging, initialize_app, credentials
from django.conf import settings
import os

cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 
            'study-zed-notifications-firebase.json'))
firebase_app = initialize_app(cred)

def send_firebase_notification(registration_id, title, body, extra_data=None):
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