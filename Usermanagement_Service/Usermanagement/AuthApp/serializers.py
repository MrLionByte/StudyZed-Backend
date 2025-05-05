import redis
import logging
from AuthApp.models import UserAddon, Email_temporary
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from AuthApp import validator
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings

redis_client = redis.StrictRedis(
    host=str(settings.REDIS_HOST), port=settings.REDIS_PORT, db=0, decode_responses=True
)

logger = logging.getLogger(__name__)

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if UserAddon.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")
        try:
            user_under_verification = Email_temporary.objects.get(email=email)
            if user_under_verification.otp != otp:
                raise serializers.ValidationError("OTP is incorrect")
            otp_expiry_time_str = user_under_verification.expires_at
            current_time = now()
            if current_time > otp_expiry_time_str:
                user_under_verification.delete()
                raise serializers.ValidationError(
                    "Otp has expired. Please request a new one and try again."
                )
            return attrs
        except Exception as e:
            logger.exception("Error in OTP SERIALIZER :", extra={'data': str(e)})


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not UserAddon.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserAddon
        fields = (
            "id",
            "username",
            "password",
            "role",
            "first_name",
            "last_name",
            "email",
        )
        extra_kwargs = {"password": {"write_only": True, "required": True}}

    def create(self, validated_data):
        user = UserAddon.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = UserAddon.objects.get(email=email)
            if not check_password(password, user.password):
                raise serializers.ValidationError(
                    {
                        "message": "Incorrect password.",
                        "auth-status": "password-failed",
                        "field": "password",
                    }
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    {
                        "message": "User is blocked",
                        "auth-status": "user-blocked",
                        "field": "status",
                    }
                )
            data["user"] = user
            return data
        except UserAddon.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "message": "User does not exist.",
                    "auth-status": "user-notexsist",
                    "field": "email",
                }
            )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        token["user_code"] = user.user_code
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        decoded_payload = AccessToken(data["access"])

        user_uid = decoded_payload["user_id"]

        user = UserAddon.objects.get(id=user_uid)

        decoded_payload["role"] = user.role
        decoded_payload["email"] = user.email
        decoded_payload["user_code"] = user.user_code

        data["access"] = str(decoded_payload)
        return data
