from django.shortcuts import render
from rest_framework import generics, status, response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import Assessments, Assessment_Questions, Answer_Options, Session
from assessment_student_side.models import StudentAssessment, StudentAssessmentResponse
from django.db import transaction
from django.db.models import F
from decimal import Decimal, DecimalException

# Create your views here.


class CreateAssessmentView(generics.CreateAPIView):
    queryset = Assessments.objects.all()
    serializer_class = AssessmentsSerializer
    
    def perform_create(self, serializer):
        assessment = serializer.save()
        return assessment


class GetAssessmentView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GetAssessmentsSerializer

    def get_queryset(self):
        session_code = self.request.GET.get('session_code', '')
        session_key = Session.objects.get(session_code=session_code)
        return Assessments.objects.filter(session_key=session_key)
    

class AddQuestionsToAssessmentView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AddQuestionsToAssessmentSerializers
    queryset = Assessment_Questions.objects.all()

class AttendedStudentsAndMark(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GetStudentSerializers
    
    def get_queryset(self):
        assessment_id = self.request.GET.get('assessment_id', '')
        if not assessment_id:
            return StudentAssessment.objects.none()
        try:
            assessment = Assessments.objects.get(id=assessment_id)
        except Assessments.DoesNotExist:
            return StudentAssessment.objects.none()
        
        return StudentAssessment.objects.filter(assessment=assessment)
    
class AttendedAssessment(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentAssessmentSerializer
    
    def get_queryset(self):
        student_id = self.request.GET.get('student_id', '')
        if not student_id:
            return StudentAssessment.objects.none()

        return StudentAssessment.objects.filter(id=student_id)

class UpdateMarkForAssessmentView(APIView):
    @transaction.atomic
    def patch(self, request):
        try:
            data = request.data

            for id, mark in data.items():
                try:
                    student_response = StudentAssessmentResponse.objects.select_for_update().get(id=id)
                    student_response.mark = mark
                    student_response.save()
                    
                    if student_response.student_assessment.score:
                        student_response.student_assessment.score += Decimal(mark)
                        student_response.student_assessment.save()
                    else:
                        student_response.student_assessment.score = Decimal(mark)
                        student_response.student_assessment.save()
                
                except StudentAssessmentResponse.DoesNotExist:
                    return Response({
                        'error': f'Response with ID {id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    print("Exception :",e)
                    return Response({
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                return Response(status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
