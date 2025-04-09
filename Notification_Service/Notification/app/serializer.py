from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.Serializer):
    id = serializers.CharField() 
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(allow_null=True, required=False)
    user_code = serializers.CharField()
    type = serializers.ChoiceField(choices=["message", "alert", "reminder", "other"])
    is_read = serializers.BooleanField(default=False)
    notified = serializers.BooleanField(default=False)
    due_time = serializers.DateTimeField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
