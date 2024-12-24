from AuthApp.models import Profile, UserAddon
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Profile
        fields = ['profile_picture', 'cover_picture', 'phone', 'user']
    
class UserAddonSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = UserAddon
        fields = ['id', 'username', 'email', 'role', 'profile', 'first_name', 'last_name']

class UploadProfilePictureSerializer(serializers.Serializer):
    file = serializers.ImageField(required=True)

class UploadCoverPictureSerializer(serializers.Serializer):
    file = serializers.ImageField(required=True)

class UpdatePhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16 ,required=True) 
    
class UserBlockSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()
    
    class Meta:
        model = UserAddon
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance