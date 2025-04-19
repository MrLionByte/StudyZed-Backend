from django.shortcuts import render
from rest_framework.views import APIView, models
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from assessment_tutor_side.models import Assessments, Session
from assessment_student_side.models import StudentAssessment
from task_student_side.models import AssignedTask
from task_tutor_side.models import Tasks
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Max,Count,Avg
from session_tutor.permissions import TutorAccessPermission

# Create your views here.

import logging
logger = logging.getLogger(__name__)

NewSerializer = ''

class StudentsAssessmentPerformancePerMonthViews(APIView):
    """ 
    API view to retrieve student performance based on their assessments per month.
    Args:
        APIView: Django REST Framework's APIView.
    Returns:
         Response: DRF Response containing student performance data in JSON format.
    """
    permission_classes = [TutorAccessPermission]
    
    def get(self, request, *args, **kwargs):
        session_code = request.GET.get('session_code')
        if not session_code:
            logger.error("Session CODE is required.")
            return Response({'error': 'Session CODE is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_code=session_code)
            if session.is_active == False:
                logger.error("Session is not active.")
                return Response({'error': 'Session is not active.'}, status=status.HTTP_400_BAD_REQUEST)
        except Session.DoesNotExist:
            logger.error("Session not found.")
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now()
        last_sixth_month = today - relativedelta(months=3)
        assessments = Assessments.objects.filter(
            session_key=session,
            start_time__gte=last_sixth_month,
            start_time__lte=today
            )
        student_assessments = StudentAssessment.objects.filter(
            assessment__in=assessments,
            # is_late_submission = False
            )
        student_data = (
            student_assessments
            .values(
                'student_session__student_code',
                'assessment__id','assessment__assessment_title'
            )
            .annotate(
                max_score_achieved=Max('score')
            )
            .order_by('student_session__student_code','assessment__id')
        )
        
        all_assessments = assessments.values_list('assessment_title', flat=True).distinct()
        unique_assessments = sorted(all_assessments)
        
        response_data = {}
        for data in student_data:
            student_code = data['student_session__student_code']
            assessment_name = data['assessment__assessment_title']
            max_score_achieved = data['max_score_achieved']
            
            if student_code not in response_data:
                response_data[student_code] = {
                    'name': student_code,
                    'data': [0] * len(unique_assessments), 
                }
            
            assessment_index = unique_assessments.index(assessment_name)
            response_data[student_code]['data'][assessment_index] = max_score_achieved
        
        response_data_list = list(response_data.values())
        
        response = {
            'year': today.year,
            'month': today.month,
            'data' : response_data_list
        }
        
        return Response(response, status=status.HTTP_200_OK)
        

class StudentsDailyAssessmentPerformancePerMonthViews(APIView):
    """ 
    API view to retrieve student performance based on their daily task per month.
    Args:
        APIView: Django REST Framework's APIView.
    Returns:
         Response: DRF Response containing student performance data in JSON format.
    """
    permission_classes = [TutorAccessPermission]
    
    def get(self, request, *args, **kwargs):
        session_code = request.GET.get('session_code')
        if not session_code:
            return Response({'error': 'Session CODE is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_code=session_code)
            if session.is_active == False:
                logger.error("Session is not active.")
                return Response({'error': 'Session is not active.'}, status=status.HTTP_400_BAD_REQUEST)
        except Session.DoesNotExist:
            logger.error("Session not found.")
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now()
        last_month = today - relativedelta(months=1)
        tasks = Tasks.objects.filter(
            session=session,
            due_date__gte=last_month,
            due_date__lte=today
            )
        student_tasks = AssignedTask.objects.filter(task__in=tasks)

        student_data = (
            student_tasks
            .values('student__student_code')
            .annotate(
                total_tasks=Count('task'),
                completed_tasks=Count('task', filter=Q(score__isnull=False)),
                on_time_tasks=Count('task', filter=Q(is_late_submission=False)),
                average_score=Avg('score')
            )
        )

        response_data = []
        for student in student_data:
            completion_rate = (student['completed_tasks'] / student['total_tasks']) * 100 if student['total_tasks'] > 0 else 0
            on_time_rate = (student['on_time_tasks'] / student['total_tasks']) * 100 if student['total_tasks'] > 0 else 0
            average_score = student['average_score'] or 0

            response_data.append({
                'student_code': student['student__student_code'],
                'completion_rate': completion_rate,
                'on_time_rate': on_time_rate,
                'average_score': average_score,
            })

        return Response(response_data, status=status.HTTP_200_OK)