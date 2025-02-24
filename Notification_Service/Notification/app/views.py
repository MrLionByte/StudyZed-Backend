from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from .models import Notification
# Create your views here.

class TestNotification(APIView):
    def post(self, request):
        data = request.data
        print(data)
        return None
    
    