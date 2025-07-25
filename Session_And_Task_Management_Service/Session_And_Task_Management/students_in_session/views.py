from rest_framework import generics, views
from rest_framework_simplejwt import authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import StudentsInSession
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import DatabaseError
from rest_framework_simplejwt.backends import TokenBackend
import jwt
from .permissions import StudentAccessPermission

# Create your views here.

import logging
logger = logging.getLogger(__name__)

class StudentEnterSessionView(generics.CreateAPIView):
    permission_classes = [StudentAccessPermission]
    queryset = StudentsInSession.objects.all()
    serializer_class = EnterSessionSerializer
    

class StudentSessionView(generics.ListAPIView):
    serializer_class = StudentSessionSerializer
    permission_classes = [StudentAccessPermission]
    
    def get_queryset(self):
        student_code = self.request.query_params.get('student_code')
        if not student_code:
            logger.error("student_code query parameter is missing.")
            raise ValidationError("student_code query parameter is required.")
        
        return StudentsInSession.objects.filter(
            student_code=student_code,session__is_rejected=False)
        
    
class MyBatchMatesInSessionView(views.APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            session_code = request.query_params.get('session_code')
            
            if not session_code:
                logger.error("session_code query parameter is missing.")
                raise ValidationError("query need session_code")
            
            session = Session.objects.get(session_code=session_code)
            
            student_codes = list(
                StudentsInSession.objects.filter(session=session, is_allowded=True)
                .values_list("student_code", flat=True)
            )
            
            return Response(student_codes, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            logger.error("Session with the given session_code does not exist.")
            return Response(
                {"error": "Session with the given session_code does not exist."}, 
                status=status.HTTP_404_NOT_FOUND)
        
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({"error": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSessionDetailsView(generics.ListAPIView):
    serializer_class = GetSessionSerializers
    permission_classes = [AllowAny]
    
    def get_queryset(self):    
        session_code = self.request.query_params.get('session_code')
        if not session_code:
            logger.error("session_code query parameter is missing.")
            raise ValidationError("session is required.")
        
        return Session.objects.filter(session_code=session_code)