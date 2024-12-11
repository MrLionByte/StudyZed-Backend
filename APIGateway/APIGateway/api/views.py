from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views import View


# Create your views here.

class APIgateView(View):
    
    def dispatch(self, request, *args, **kwargs):
        services = kwargs.get('services')
        print("GOTTT", services)
        path = request.path
        print(path)
    