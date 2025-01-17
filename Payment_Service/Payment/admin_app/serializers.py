from rest_framework import serializers
from session_buy.models import Subscription, Payment

class AllPaymentOfSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model= Payment
        fields = "__all__"

class AdminSessionPaymentViewSerializer(serializers.ModelSerializer):
    payment_set = AllPaymentOfSubscriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = ['subscription_id', 'tutor_code', 'subscription_type', 'session_code',
                    'created_at', 'expiry_time', 'is_active',
                    'payment_set']
    
    
    