from firebase_admin import credentials, messaging, initialize_app

class FCMServices:
    def __init__(self):
        pass

    def send_message(self, title, message, tokens):
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message
                ),
                tokens=tokens
            )
            response = messaging.send_multicast(message)
            return {"success": True, "message": response}
        except Exception as e:
            return {"error": str(e)}