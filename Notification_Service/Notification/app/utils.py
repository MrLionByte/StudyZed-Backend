from firebase_admin import messaging

def send_fcm_notification(token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,body=body),
            token=token
        )
        response = messaging.send(message)
        return {"success": True, "message_id": response}
    except Exception as e:
        return {"error": str(e)}
        