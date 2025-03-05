from rest_framework import serializers
from datetime import datetime, timezone
from .models import LiveSessionOneToOne, LiveSessionGroup
from Chat.models import User, OpenChatRoom

class LiveSessionOneToOneSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    caller = serializers.CharField()
    receiver = serializers.CharField()
    session_code = serializers.CharField()
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    ended_at = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=['scheduled', 'ongoing', 'ended', 'missed'])

    def to_representation(self, instance):
        """To get caller_id and receiver_id instead of User objects in get Method"""
        data = super().to_representation(instance)

        data['caller'] = instance.caller.user_id if instance.caller else None
        data['receiver'] = instance.receiver.user_id if instance.receiver else None

        return data

    def create(self, validated_data):
        """Create and return a new LiveSessionOneToOne instance."""
        return LiveSessionOneToOne(**validated_data).save()

    def update(self, instance, validated_data):
        """Update an existing LiveSessionOneToOne instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class LiveSessionGroupSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    session = serializers.CharField()
    host = serializers.CharField()
    participants = serializers.ListField(child=serializers.CharField(), required=False)
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    ended_at = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=['scheduled', 'ongoing', 'ended', 'missed'])

    def create(self, validated_data):
        """Create and return a new LiveSessionGroup instance."""
        return LiveSessionGroup(**validated_data).save()

    def update(self, instance, validated_data):
        """Update an existing LiveSessionGroup instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
