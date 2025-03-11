from datetime import datetime, timezone, timedelta
from Chat.models import OpenChatRoom, User
from rest_framework.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from mongoengine import (Document, StringField, IntField,
                         ReferenceField, DateTimeField, 
                         ListField, CASCADE, BooleanField)


class LiveSessionOneToOne(Document):
    caller = ReferenceField(User, required=True)
    receiver = ReferenceField(User, required=True)
    started_at = DateTimeField(null=True)
    ended_at = DateTimeField(null=True) 
    status = StringField(choices=['live', 'ended'], default='live')
    
    def start_call(self):
        """Activates the session if the scheduled time has arrived."""
        now = datetime.now(timezone.utc)
        self.started_at = now
        self.status = 'live'
        self.save()
    
    def end_call(self):
        """Marks the session as ended and records the end time."""
        self.ended_at = datetime.now(timezone.utc)
        self.status = 'ended'
        self.save()

    def __str__(self):
        return f"One-to-One Call: {self.caller} -> {self.receiver} ({self.status})"

class LiveSessionGroup(Document):
    session = StringField(required=True)
    host = ReferenceField(User, required=True)
    participants = ListField(ReferenceField(User), null=True)
    description = StringField(null=True)
    started_at = DateTimeField(null=True)
    scheduled_time = StringField(null=True)
    ended_at = DateTimeField(null=True)
    status = StringField(choices=['scheduled','live', 'ended'], default='scheduled')
    
    
    def start_call(self):
        """Activates the session if the scheduled time has arrived."""
        self.started_at = datetime.now(timezone.utc)
        self.status = 'live'
        self.save()

    def add_participants(self, user):
        """Adds a user to the session."""
        if user not in self.participants:
            self.participants.append(user)
            self.save()

    def remove_participant(self, user):
        """Removes a user from the session."""
        if user in self.participants:
            self.participants.remove(user)
            self.save()

    def end_call(self):
        """Marks the session as ended."""
        self.ended_at = datetime.now(timezone.utc)
        self.status = 'ended'
        self.save()

    def __str__(self):
        return f"Group Call in {self.session} ({self.status})"