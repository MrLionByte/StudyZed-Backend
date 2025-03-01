from rest_framework import serializers
from .models import OneToOneMessage, User
from mongoengine import DateTimeField

class OneToOneMessageSerializer(serializers.Serializer):
    sender = serializers.CharField(source='sender.user_code')
    recipient = serializers.CharField(source='recipient.user_code')
    content = serializers.CharField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        fields = ['sender', 'recipient', 'content', 'timestamp']
        
