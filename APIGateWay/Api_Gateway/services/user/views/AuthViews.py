from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import requests
from rest_framework import status
from django.conf import settings

logging = logging.getLogger(__name__)
USER_SERVICE_URL = "http://127.0.0.1:8005/"

class UserAuthAppView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    
    def options(self, request, *args, **kwargs):
        print(request.data)
        # Handle OPTIONS requests (CORS preflight)
        return Response(headers={
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        })
    
    def get(self, request, path, *args, **kwargs):
        print(request.data)
        logging.info("Received user management request")
        user_url = f"{USER_SERVICE_URL}/auth-app/{path}"
        response = requests.post(user_url, json=request.data, headers=dict(request.headers))
        return Response(
            data=response['data'],
            status=response['status_code']
        )
        
    def post(self, request, path, *args, **kwargs):
        print(request.data)
        print(path)
        user_url = f"{USER_SERVICE_URL}/auth-app/{path}"
        response = requests.post(user_url, json=request.data, headers=dict(request.headers))
        
        return Response(response.json(), status=response.status_code)
    
    def put(self, request, path, *args, **kwargs):
        print(request.data)
        user_url = f"{USER_SERVICE_URL}/auth-app/{path}"
        response = requests.put(user_url, json=request.data, headers=dict(request.headers))
        return Response(response.json(), status=response.status_code)
    
    def delete(self, request, path, *args, **kwargs):
        print(request.data)
        user_url = f"{USER_SERVICE_URL}/auth-app/{path}"
        response = requests.delete(user_url, json=request.data, headers=dict(request.headers))
        return Response(response.json(), status=response.status_code)
    
    def patch(self, request, path, *args, **kwargs):
        print(request.data)
        user_url = f"{USER_SERVICE_URL}/auth-app/{path}"
        response = requests.patch(user_url, json=request.data, headers=dict(request.headers))
        return Response(response.json(), status=response.status_code)
        
        
