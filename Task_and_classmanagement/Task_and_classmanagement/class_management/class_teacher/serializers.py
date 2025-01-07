from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

