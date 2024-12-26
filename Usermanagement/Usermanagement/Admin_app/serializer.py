from AuthApp.models import UserAddon
from rest_framework import serializers

class UserBlockSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()
    
    class Meta:
        model = UserAddon
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance