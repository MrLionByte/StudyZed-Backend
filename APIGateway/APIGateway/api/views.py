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
        try:
            token = request.headers.get('Authorization')
            if not token:
                response = self.signup_api(request)
                print(response)
                return JsonResponse(
                {
                    'response': str(response)
                }
            )
            else:
                token = token.replace("Bearer ", "")
                secret_key = 'django-insecure-3=e8t28jwtmlds(kq1qfu)8&1!2ysi7hm8l^(8&q@8&w2r0-b9'
                decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            print(decoded_token)
            print("PATH :",path, service, token)
            return JsonResponse(
                {
                    'message': decoded_token,
                    "service": service,
                    "path": path,
                }
            )
        except Exception as e:
            print("GATEWAY Error :", str(e))
            return JsonResponse(
                {
                    'error': str(e)
                }
            )

    def signup_api(self, request):
        url = "http://localhost:8005/auth-app/user-email/"
        try:
            response = request.post(url, json=request.body)
            print("response :",response)
            return response
        except Exception as e:
            print("ERRROR SINGN :",e)
            return JsonResponse(
                {
                    'error': str(e)
                }
            )

# class APIgateView(View):

#     def dispatch(self, request, *args, **kwargs):
#         services = kwargs.get("services")
#         print("GOTTT", services)
#         path = request.path
#         print(path)



