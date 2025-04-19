import logging
from django.shortcuts import render
from rest_framework import views, generics ,status
from .models import (Session, StudentsInSession, StudentAssessmentResponse, 
                     StudentAssessment, Assessments, Assessment_Questions,
                     Answer_Options)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound, AuthenticationFailed, ParseError
from datetime import datetime
from .jwt_utils import decode_jwt_token
import jwt
from django.shortcuts import get_object_or_404
from .serializers import *
from session_tutor.producer import kafka_producer
# Create your views here.

logger = logging.getLogger(__name__)

class GetAssessmentsForStudentViews(views.APIView):
    def get(self, request):
        session_code = request.GET.get("session_code")

        try:
            session = Session.objects.get(session_code=session_code)
            if not session.is_active:
                logger.error(f"Session with code {session_code} is not active")
                return Response({
                    'error': 'Session is not active'
                }, status=status.HTTP_400_BAD_REQUEST)
            assessments = Assessments.objects.filter(session_key=session)
            serializer = AssessmentsSerializer(assessments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            logger.error(f"Session with code {session_code} not found")
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in GetAssessmentsForStudentViews: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendAssessmentViews(views.APIView):
    def post(self, request):
        data = request.data.get("data")
        assessment_id = request.data.get("assessment_id")
        
        try:
            student = decode_jwt_token(request)
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Error in AttendAssessmentViews: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            assessment_instance = Assessments.objects.get(id=assessment_id)
            student_code = student.get("user_code")
            student = StudentsInSession.objects.get(student_code=student_code)
            student_assessment = StudentAssessment.objects.create(
                student_session = student,
                assessment = assessment_instance,
                completed_on = datetime.now(),
                is_completed = True                
            )
            for question in data:
                question_instance = Assessment_Questions.objects.get(id=question.get("questionId"))
                assessment_response = StudentAssessmentResponse.objects.create(
                    student_assessment = student_assessment,
                    question = question_instance,
                )
                if question["questionType"] == "OPEN":
                    assessment_response.open_response = question["answer"]
                    assessment_response.save()
                    
                else:
                    opted = Answer_Options.objects.get(id=question["answer"])
                    assessment_response.selected_option = opted
                    assessment_response.save()
                    
            data = {
                    "message": f"assessment {student_assessment.assessment.assessment_title} submitted by :{student_code}",
                    "title": student_assessment.assessment.assessment_title,
                    "tutor_code": student_assessment.assessment.session_key.tutor_code,
                    "type": "alert",
            }
            kafka_producer.producer_message('assessment_attend', student_code, data)
            return Response({'2122'},status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            logger.error(f"Error in AttendAssessmentViews: {str(e)}")
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

class GetAttendedAssessmentsView(generics.ListAPIView):
    serializer_class = GetAttendedAssessmentsSerializers
    permission_classes = [AllowAny]
    queryset = StudentAssessment.objects.all()
    
    def get_queryset(self):
        try:
            user_data = decode_jwt_token(self.request)
            user = StudentsInSession.objects.get(
                student_code = user_data['user_code'])
            return StudentAssessment.objects.filter(student_session=user)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        
        except StudentsInSession.DoesNotExist:
            raise NotFound("User not found")
        
        except Exception as e:
            logger.error(f"Error in GetAttendedAssessmentsView: {str(e)}")
            raise ParseError(str(e))