from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt import authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Session
from students_in_session.models import StudentsInSession
from .serializers import (
    CreateSessionSerializers, 
    TutorSessionSerializer, 
    AllStudentInSessions, 
    ApprovedStudentsInSessions,
    UpdateSessionSerializer,
    )
from rest_framework.response import Response
from rest_framework import status
from .utils.responses import api_response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError
from .producer import kafka_producer
from .permissions import TutorAccessPermission
from .utils.jwt_utils import decode_jwt_token
from .custompagination import CursorPaginationWithOrdering
from rest_framework.views import APIView


import logging
logger = logging.getLogger(__name__)

class CreateSessionView(generics.CreateAPIView):
    serializer_class = CreateSessionSerializers
    permission_classes = [TutorAccessPermission]
    queryset = Session.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            instance = serializer.save() 
            
            response_data = serializer.data
            response_data["session_code"] = instance.session_code
            response_data['created_on'] = instance.created_at.isoformat()
            kafka_producer.producer_message('create-session', response_data["session_code"], response_data)
            return api_response(
                status_code =status.HTTP_201_CREATED,
                message = 'Session created successfully',
                data = serializer.data,
                auth_status=None,
                errors=None
            )
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Validation failed',
                data=None,
                auth_status=None,
                errors=e.detail 
            ) 
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Database error occurred',
                data=None,
                auth_status=None,
                errors=str(e)
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return api_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='An unexpected error occurred',
                data=None,
                auth_status=None,
                errors=str(e)
            )


class RenewSessionSubscription(generics.UpdateAPIView):
    serializer_class = UpdateSessionSerializer
    permission_classes = [TutorAccessPermission]
    
    def get_queryset(self):
        session_code = self.request.data.get('session_code')
        if not session_code:
            logger.error("session_code is required.")
            raise ValidationError("session_code is required.")

        try:
            return Session.objects.filter(session_code=session_code)
        except Exception as e:
            logger.error(f"Error fetching sessions: {e}")
            raise ValidationError("An error occurred while fetching sessions.")
            
class GetSessionView(generics.RetrieveAPIView):
    serializer_class = CreateSessionSerializers
    queryset = Session.objects.all()
    permission_classes = [TutorAccessPermission]
    # pagination_class = ""


class TutorsSessionsView(generics.ListAPIView):
    serializer_class = TutorSessionSerializer
    permission_classes = [TutorAccessPermission]
    pagination_class = CursorPaginationWithOrdering
    
    def get_queryset(self):
        tutor_code = self.request.query_params.get('tutor_code')
        if not tutor_code:
            raise ValidationError("tutor_code query parameter is required.")

        try:
            return Session.objects.filter(tutor_code=tutor_code).order_by('created_at')
        except Exception as e:
            logger.error(f"Error fetching sessions: {e}")
            raise ValidationError("An error occurred while fetching sessions.")

class StudentsInSessionView(generics.ListAPIView):
    serializer_class = AllStudentInSessions
    permission_classes = [TutorAccessPermission]
    
    def get_queryset(self):
        session_code = self.request.query_params.get('session_code')
        user_data = decode_jwt_token(self.request)
        tutor_code = user_data.get("user_code")
        if not session_code:
            logger.error("session_code query parameter is required.")
            raise ValidationError("tutor_code query parameter is required.")
        session = Session.objects.get(session_code=session_code)
        if not session.tutor_code == tutor_code:
            logger.error("session_not_belong")
            raise PermissionError("session_not_belong")
        return StudentsInSession.objects.filter(session=session)

class ApproveStudentToSessionView(generics.UpdateAPIView):
    queryset = StudentsInSession.objects.all()
    permission_classes = [TutorAccessPermission]
    
    def update(self, request, *args, **kwargs):
        student = self.get_object()
        student.is_allowded = True
        student.save()
        return Response({"message": f"Successfully approved session {student.student_code}",
                        'student_code': f'{student.student_code}' },
                        status=status.HTTP_202_ACCEPTED)

class StudentsDataInSessionView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            session_code = request.query_params.get('session_code')
            user_data = decode_jwt_token(request)
            tutor_code = user_data.get("user_code")
            
            if not session_code:
                logger.error("query need session_code")
                raise ValidationError("query need session_code")
            
            session = Session.objects.get(session_code=session_code)
            if session.tutor_code != tutor_code:
                logger.error("Session does not belong to this tutor.")
                raise PermissionDenied("Session does not belong to this tutor.")
            
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
        
        except PermissionDenied as e:
            logger.error(f"Permission denied: {str(e)}")
            return Response({"error": str(e)}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateSessionViews(generics.UpdateAPIView):
    serializer_class = UpdateSessionSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        try:
            session_code = self.request.query_params.get("session_code")
            session = Session.objects.get(session_code=session_code)
            return session
        except Session.DoesNotExist:
            logger.error("Session not found.")
            raise NotFound("Session not found.")
    
    def patch(self, request):
        session_to_be_updated = self.get_object()
        serializer = self.get_serializer(
            session_to_be_updated, data=request.data, partial=True
        )
        if serializer.is_valid():
            if 'image' in request.FILES:
                session_to_be_updated.image = request.FILES['image']
                session_to_be_updated.save()
                
            serializer.save()
            return Response(serializer.data, status=200)
        
        logger.error("Invalid data provided for session update.")
        return Response(serializer.errors, status=400)
    
    def get(self, request, *args, **kwargs):
        session_code = request.query_params.get("session_code")
        if not session_code:
            logger.error("session_code is required.")
            return Response({"error": "session_code is required"}, status=400)

        try:
            session = Session.objects.get(session_code=session_code)
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=200)
        except Session.DoesNotExist:
            logger.error("Session not found.")
            return Response({"error": "Session not found"}, status=404)