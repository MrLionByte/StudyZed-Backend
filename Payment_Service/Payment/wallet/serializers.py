from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Wallet, WalletTransactions


# class SubscriptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subscription
#         # fields = ['subscription_id', 'tutor_code', 'subscription_type', 'sessions_purchased']
#         fields = ('tutor_code', 'subscription_type', 'sessions_purchased', 'sessions_remaining')

# class PaymentSerializer(serializers.ModelSerializer):
#     subscription_key = serializers.PrimaryKeyRelatedField(queryset=Subscription.objects.all())
#     renew = serializers.BooleanField(default=False)
#     print("VALID SERDATA :" ,subscription_key)
    
#     class Meta:
#         model = Payment
#         fields = ('subscription_key', 'amount', 'reference_id', 'status', 'renew')

#     def create(self, validated_data):
#         print("VALID DATA :" ,validated_data)
#         renew = validated_data.pop('renew')
#         subscription = validated_data['subscription_key']
        
#         if renew:
#             subscription.renew_subscription(
#                 subscription_type = validated_data.get('subscription_type'),
#                 sessions_purchased = validated_data.get('sessions_purchased')
#             )
#         return Payment.objects.create(**validated_data)

class WalletTransactionsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransactions
        fields = ['tranaction_type', 'tickets', 'amount', 'note', 'status', 'currency', 'transaction_id', 'tranaction_date']
    
class WalletViewSerializer(serializers.ModelSerializer):
    wallet_transactions = WalletTransactionsViewSerializer(many=True, readonly=True)    
    class Meta:
        model = Wallet
        fields = ['account_number', 'balance', 'is_blocked', 'updated_at', 'currency_mode', 'wallet_transactions']
