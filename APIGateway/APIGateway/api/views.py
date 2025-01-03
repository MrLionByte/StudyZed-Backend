from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views import View
from django.http import JsonResponse
import jwt
from django.conf import settings


# Create your views here.

class APIgateView(View):
    
    @csrf_exempt
    def dispatch(self, request, service=None, path=None, *args, **kwargs):
        token = request.headers.get('Authorization')
        secret_key = 'django-insecure-3=e8t28jwtmlds(kq1qfu)8&1!2ysi7hm8l^(8&q@8&w2r0-b9'
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        print(decoded_token)
        return JsonResponse(
            {
                'message': decoded_token,
                "service": service,
                "path": path,
            }
        )


# class APIgateView(View):

#     def dispatch(self, request, *args, **kwargs):
#         services = kwargs.get("services")
#         print("GOTTT", services)
#         path = request.path
#         print(path)



