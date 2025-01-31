from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt import authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Session
from students_in_session.models import StudentsInSession
from .serializers import CreateSessionSerializers, TutorSessionSerializer, AllSessionInSessions
from rest_framework.response import Response
from rest_framework import status
from .utils.responsses import api_response
from rest_framework.exceptions import ValidationError
from django.db import DatabaseError
from .producer import kafka_producer
from .permissions import TutorAccessPermission
from .utils.jwt_utils import decode_jwt_token

# Create your views here.

class CreateSessionView(generics.CreateAPIView):
    serializer_class = CreateSessionSerializers
    permission_classes = [TutorAccessPermission]
    queryset = Session.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            instance = serializer.save() #To save data in db
            
            response_data = serializer.data
            response_data["session_code"] = instance.session_code
            response_data['created_on'] = instance.created_at.isoformat()
            print("Session Data before Kafka:", response_data)
            kafka_producer.producer_message('create-session', response_data["session_code"], response_data)
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
    permission_classes = [TutorAccessPermission]


class TutorsSessionsView(generics.ListAPIView):
    serializer_class = TutorSessionSerializer
    permission_classes = [TutorAccessPermission]
    
    def get_queryset(self):
        print("111111")
        tutor_code = self.request.query_params.get('tutor_code')
        print("SESSIOn CODE :",tutor_code)
        if not tutor_code:
            raise ValidationError("tutor_code query parameter is required.")
        
        return Session.objects.filter(tutor_code=tutor_code)


class StudentsInSessionView(generics.ListAPIView):
    serializer_class = AllSessionInSessions
    permission_classes = [TutorAccessPermission]
    
    def get_queryset(self):
        session_code = self.request.query_params.get('session_code')
        user_data = decode_jwt_token(self.request)
        tutor_code = user_data.get("user_code")
        if not session_code:
            raise ValidationError("tutor_code query parameter is required.")
        session = Session.objects.get(session_code=session_code)
        if not session.tutor_code == tutor_code:
            raise PermissionError("session_not_belong")
        return StudentsInSession.objects.filter(session=session)

class ApproveStudentToSessionView(generics.UpdateAPIView):
    queryset = StudentsInSession.objects.all()
    permission_classes = [TutorAccessPermission]
    
    def update(self, request, *args, **kwargs):
        student = self.get_object()
        print("GET OBJ :", student, student.is_allowded)
        student.is_allowded = True
        print(student.is_allowded)
        student.save()
        print(student.is_allowded)
        return Response({"message": f"Successfully approved session {student.student_code}",
                        'student_code': f'{student.student_code}' },
                        status=status.HTTP_202_ACCEPTED)
    
