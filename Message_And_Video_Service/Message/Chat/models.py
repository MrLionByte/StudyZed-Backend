from django.db import models
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings
from datetime import datetime, timezone

from mongoengine import (Document, StringField, IntField,
                         ReferenceField, DateTimeField, 
                         ListField, CASCADE, BooleanField)

class User(Document):
    user_id = IntField(unique=True)
    user_code = StringField()
    user_role = StringField()
    email = StringField()

    @property
    def is_anonymous(self):
        return False
        
    @property
    def id(self):
        return self.user_id
    
    @property
    def code(self):
        return self.user_code
    
class OneToOneMessage(Document):
    sender = ReferenceField(User, reverse_delete_rule=2)  
    recipient = ReferenceField(User, reverse_delete_rule=2) 
    content = StringField(required=True) 
    timestamp = DateTimeField(default=datetime.now(timezone.utc))  

    meta = {
        'ordering': ['timestamp']
    }

    def __str__(self):
        return f"{self.sender.email} ==>> {self.recipient.email}"


class OpenChatRoom(Document):
    session_code = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    members = ListField(ReferenceField(User))
    
    def __str__(self):
        return self.session_code  

class OpenChatMessage(Document):
    sender = ReferenceField(User, required=True)  
    recipient = ReferenceField(User, required=True)  
    community = ReferenceField(OpenChatRoom, required=True)
    content = StringField(required=True) 
    timestamp = DateTimeField(default=datetime.now(timezone.utc))  
    is_deleted = BooleanField(default=False)  

    meta = {
        'ordering': ['timestamp']
    }

    def __str__(self):
        return f"{self.sender.email} ==>> {self.recipient.email} in {self.community.name}: {self.content} (Deleted: {self.is_deleted})"

    def delete_message(self):
        if self.recipient.user_role == 'teacher':
            self.is_deleted = True
            self.save()
