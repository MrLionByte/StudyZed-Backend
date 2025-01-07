from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Payment, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        # fields = ['subscription_id', 'tutor_code', 'subscription_type', 'sessions_purchased']
        fields = {'tutor_code', 'subscription_type', 'sessions_purchased'}

class PaymentSerializer(serializers.ModelSerializer):
    subscription_key = serializers.PrimaryKeyRelatedField(queryset=Subscription.objects.all())
    class Meta:
        model = Payment
        fields = {'subscription_key', 'amount', 'reference_id', 'status'}
