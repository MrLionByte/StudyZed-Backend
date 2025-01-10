from django.shortcuts import render
from .models import Wallet, WalletTransactions
from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.

class StudentWalletView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletViewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        wallet = Wallet.objects.prefetch_related(
            serializers.Prefetch(
                'wallet_transactions',
                queryset=WalletTransactions.objects.all().order_by(
                    '-transaction_date')[:10]
            )
        )
        return wallet

class TutorWalletView(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletViewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        wallet = Wallet.objects.prefetch_related(
            serializers.Prefetch(
                'wallet_transactions',
                queryset=WalletTransactions.objects.all().order_by(
                    '-transaction_date')[:10]
            )
        )
        return wallet
    
    