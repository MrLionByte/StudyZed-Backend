from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt import authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Session
from .serializers import CreateSessionSerializers
from rest_framework.response import Response
from rest_framework import status
from .utils.responsses import api_response
from rest_framework.exceptions import ValidationError
from django.db import DatabaseError
from .producer import kafka_producer

# Create your views here.

class CreateSessionView(generics.CreateAPIView):
    serializer_class = CreateSessionSerializers
    queryset = Session.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            response_data = serializer.data
            response_data["session_code"] = instance.session_code
            response_data['created_on'] = instance.created_at.isoformat()
            print("Session Data before Kafka:", response_data)
            kafka_producer.producer_message('create-session', response_data["session_code"], response_data)
            instance = serializer.save() #To save data in db
            return api_response(
                status_code =status.HTTP_201_CREATED,
                message = 'Session created successfully',
                data = serializer.data,
                auth_status=None,
                errors=None
            )
            
        except ValidationError as e:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Validation failed',
                data=None,
                auth_status=None,
                errors=e.detail 
            ) 
        except DatabaseError as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Database error occurred',
                data=None,
                auth_status=None,
                errors=str(e)
            )
        
        except Exception as e:
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='An unexpected error occurred',
                data=None,
                auth_status=None,
                errors=str(e)
            )
            
            
class GetSessionView(generics.RetrieveAPIView):
    serializer_class = CreateSessionSerializers
    queryset = Session.objects.all()
    permission_classes = [AllowAny]

