from AuthApp.models import UserAddon
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from AuthApp import validator
from django.utils.timezone import now
from datetime import datetime


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if UserAddon.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        session_data = self.context["request"].session.get("validationsteps", {})
        if not session_data:
            raise serializers.ValidationError("OTP is not found. Please request for a new otp")
        if email != session_data.get("email",):
            raise serializers.ValidationError("Email does not match")
        if otp!= str(session_data.get("otp")):
            raise serializers.ValidationError("OTP is incorrect")
        expires = datetime.fromisoformat(session_data.get("expires_at"))
        if now() > expires:
            raise serializers.ValidationError("OTp has expired. Please request a new one and try again.")
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if the email exists in the database
        if not UserAddon.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    role = serializers.CharField(required=True)  
    first_name = serializers.CharField(required=True) 
    last_name = serializers.CharField(required=False)  
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(required=True) 
    
    class Meta:
        model = UserAddon
        fields = ('id', 'username', 'email', 'password', 'role', 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = UserAddon.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
