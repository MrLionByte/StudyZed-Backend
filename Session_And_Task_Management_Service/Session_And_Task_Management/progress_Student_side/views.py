from django.shortcuts import render
from rest_framework.views import APIView, models
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from assessment_tutor_side.models import Assessments, Session
from assessment_student_side.models import StudentAssessment
from task_student_side.models import AssignedTask, StudentsInSession
from task_tutor_side.models import Tasks
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Max,Count,Avg
from session_tutor.utils.jwt_utils import decode_jwt_token
from json import dumps
import calendar
from students_in_session.permissions import StudentAccessPermission
# Create your views here.


import logging
logger = logging.getLogger(__name__)

class StudentPersonalAssessmentPerformanceView(APIView):
    """ 
    API view to retrieve student performance based on their assessments per month.
    Args:
        APIView: Django REST Framework's APIView.
    Returns:
         Response: DRF Response containing student performance data in JSON format.
    """
    
    permission_classes = [StudentAccessPermission]
    
    def get(self, request, *args, **kwargs):
        session_code = request.GET.get('session_code')
        user_data = decode_jwt_token(request)
        
        if not session_code:
            return Response({'error': 'Session CODE is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_code=session_code)
            if session.is_active == False:
                return Response({'error': 'Session is not active.'}, status=status.HTTP_400_BAD_REQUEST)
            StudentsInSession.objects.get(
                session=session,student_code=user_data['user_code']) 
        
        except Session.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except StudentsInSession.DoesNotExist:
            return Response({'error': 'Student not found in session.'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now()
        last_sixth_month = today - relativedelta(months=3)
        assessments = Assessments.objects.filter(
            session_key=session,
            start_time__gte=last_sixth_month,
            start_time__lte=today
            )
        student_assessments = StudentAssessment.objects.filter(
            assessment__in=assessments,
            student_session__student_code=user_data['user_code']
            # is_late_submission = False
            ).annotate(
                total_mark=F('assessment__total_mark'),
                obtained_mark=F('score')
            )
        
        response_data = {
        "categories": [],  
        "marks_obtained": [],  
        "marks_lost": [] 
        }
        for assessment in student_assessments:
            response_data["categories"].append(assessment.assessment.assessment_title)
            response_data["marks_obtained"].append(assessment.obtained_mark)
            response_data["marks_lost"].append(assessment.total_mark - assessment.obtained_mark)

        response = {
            'year': today.year,
            'month': today.month,
            'data' : response_data
        }
        
        return Response(response, status=status.HTTP_200_OK)
    
    
class StudentPersonalTaskPerformanceView(APIView):
    """ 
    API view to retrieve student performance based on their assessments per month.
    Args:
        APIView: Django REST Framework's APIView.
    Returns:
         Response: DRF Response containing student performance data in JSON format.
    """
    
    permission_classes = [StudentAccessPermission]
    
    def get(self, request, *args, **kwargs):
        session_code = request.GET.get('session_code')
        user_data = decode_jwt_token(request)
        
        if not session_code:
            return Response({'error': 'Session CODE is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_code=session_code)
            StudentsInSession.objects.get(
                session=session,student_code=user_data['user_code']) 
        
        except Session.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except StudentsInSession.DoesNotExist:
            return Response({'error': 'Student not found in session.'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        tasks = Tasks.objects.filter(
            session=session,
            due_date__gte=first_day_of_month,
            due_date__lt=today
            )
        
        student_tasks = AssignedTask.objects.filter(
            task__in=tasks,
            student__student_code=user_data['user_code']
            # is_late_submission = False
            )
        total_tasks = tasks.count()
        submitted_tasks = student_tasks.count()
        missed_tasks = total_tasks - submitted_tasks
        
        assigned_days = tasks.values("due_date").distinct().count()
        unassigned_days = today.day - assigned_days
        
        total_score = student_tasks.aggregate(
            total=models.Sum('score'))['total'] or 0
        lost_score = total_tasks * 10 - total_score
        
        response_data = {
            "attended_task": [missed_tasks, submitted_tasks],
            "total_task": [unassigned_days, assigned_days],
            "task_score_ratio": [lost_score, total_score]
        }
        
        return Response(response_data, status=status.HTTP_200_OK)