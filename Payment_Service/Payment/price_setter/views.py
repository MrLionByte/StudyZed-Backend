from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.permissions import AllowAny

from .models import PriceOfSession, CouponForSession
from .serializer import GetAllSubSerializer, UpdatePriceSerializer
# Create your views here.

class ChangeSubscriptionAmountView(generics.UpdateAPIView):
    queryset = PriceOfSession.objects.all().order_by('duration')
    permission_classes = [AllowAny]
    serializer_class = UpdatePriceSerializer

class GetAllSubscriptionAmountsView(generics.ListAPIView):
    queryset = PriceOfSession.objects.all().order_by('duration')
    permission_classes = [AllowAny]
    serializer_class = GetAllSubSerializer