from mongoengine import Document, StringField, BooleanField, DateTimeField, ReferenceField
from datetime import datetime, timezone

class Notification(Document):
    title = StringField(required=True, max_length=255)
    message = StringField()
    user_code = StringField() # To whom the notification for
    type = StringField(required=True, choices=["message", "alert", "reminder", "other"], default="other")
    
    is_read = BooleanField(default=False)
    notified = BooleanField(default=False) 
    due_time = DateTimeField()
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "indexes": [
            "user_code",
            "is_read",
            "created_at",
            "due_time",
            {"fields": ["created_at"], "expireAfterSeconds": 604800}  # 7 days
        ],
        "ordering": ["-created_at"]
    }

    def mark_as_read(self):
        """Marks the notification as read efficiently."""
        self.update(set__is_read=True)

    def __str__(self):
        return f"{self.title} - {self.user_code}"
