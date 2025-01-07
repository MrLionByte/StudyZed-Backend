from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import PaymentSerializer
from .models import Payment
# Create your views here.


class SubscriptionPaymentView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()