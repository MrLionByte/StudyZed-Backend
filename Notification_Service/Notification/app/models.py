from django.db import models
from django.contrib.auth.models import User
from mongoengine import Document, StringField, BooleanField, DateTimeField, ReferenceField
from datetime import datetime, timezone

class UserFCMToken(Document):
    user_code = StringField(required=True, unique=True)
    fcm_token = StringField(required=True)

    meta = {"indexes": ["user_code"]}


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
            "due_time",
            {"fields": ["created_at"], "expireAfterSeconds": 604800} 
        ],
        "ordering": ["-created_at"],
        "index_background": True 
    }

    def mark_as_read(self):
        self.update(set__is_read=True)

    def __str__(self):
        return f"{self.title} - {self.user_code}"