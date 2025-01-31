from rest_framework import generics
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

class StudentEnterSessionView(generics.CreateAPIView):
    print("ASDASDSADASD")
    permission_classes = [StudentAccessPermission]
    queryset = StudentsInSession.objects.all()
    serializer_class = EnterSessionSerializer

class StudentSessionView(generics.ListAPIView):
    serializer_class = StudentSessionSerializer
    permission_classes = [StudentAccessPermission]
    
    def get_queryset(self):
        print("111111")
        student_code = self.request.query_params.get('student_code')
        if not student_code:
            raise ValidationError("student_code query parameter is required.")
        
        return StudentsInSession.objects.filter(student_code=student_code)