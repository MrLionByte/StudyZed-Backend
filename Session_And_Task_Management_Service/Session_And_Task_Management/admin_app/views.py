import logging
from django.shortcuts import render
from rest_framework import generics, exceptions, status
from rest_framework.response import Response
from session_tutor.models import Session
from .serializers import (SeeSessionToApproveSerializers, ApproveSessionSerializer,
        SessionSerializer, AssessmentSerializer, TaskSerializer)
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from django.db.models import Count, Avg, Max, Min, F, Q
from django.utils import timezone
from datetime import timedelta
from task_tutor_side.models import Tasks
from assessment_tutor_side.models import Assessments
# Create your views here.


logger = logging.getLogger(__name__)

class AllSessionToApproveView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=False)
    serializer_class = SeeSessionToApproveSerializers


class ApproveSessionView(generics.UpdateAPIView):
    queryset = Session.objects.all()
    # serializer_class = ApproveSessionSerializer

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        session.is_active = True
        session.start_date = now() + relativedelta(days=+1)
        session.save()
        return Response(
            {
                "message": f"Successfully approved session {session.session_name}",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AllActiveSessionsView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=True)
    serializer_class = SeeSessionToApproveSerializers


class AllBlockedSessionsView(generics.ListAPIView):
    queryset = Session.objects.filter(is_active=False)
    serializer_class = SeeSessionToApproveSerializers


class BlockASessionView(generics.UpdateAPIView):
    queryset = Session.objects.filter(is_active=True)

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response(
            {
                "message": f"Successfully Blocked session {session.session_name}",
            },
            status=status.HTTP_202_ACCEPTED,
        )
        

class DashboardAPIView(APIView):
    """
    API view that provides all dashboard data 
    """
    def get(self, request):
        now = timezone.now()
        end_date = now.date()
        start_date = end_date - timedelta(days=30)
        
        active_sessions_count = Session.objects.filter(is_active=True).count()
        
        assessment_stats = self._get_assessment_stats(start_date, end_date)
        
        task_summary = self._get_task_summary(now)
        
        assessment_analytics = self._get_assessment_analytics(start_date)
        
        return Response({
            'session_data': {
                'active_count': active_sessions_count,
                'recent_sessions': self._get_recent_sessions()
            },
            'assessment_data': assessment_stats,
            'task_data': task_summary,
            'analytics': assessment_analytics
        }, status=status.HTTP_200_OK)
    
    def _get_assessment_stats(self, start_date, end_date):
        dates = []
        counts = []
        avg_scores = []
        
        current_date = start_date
        while current_date <= end_date:
            day_assessments = Assessments.objects.filter(created_on=current_date)
            count = day_assessments.count()
            avg_score = day_assessments.aggregate(avg_score=Avg('total_mark'))['avg_score'] or 0
            
            dates.append(current_date.strftime('%Y-%m-%d'))
            counts.append(count)
            avg_scores.append(round(avg_score, 1))
            
            current_date += timedelta(days=1)
        
        return {
            'dates': dates,
            'counts': counts,
            'avg_scores': avg_scores
        }
    
    def _get_task_summary(self, now):

        tasks = Tasks.objects.select_related('session').all()
        
        serializer = TaskSerializer(tasks, many=True)
        task_data = serializer.data
        
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(notified=True).count()
        overdue_tasks = tasks.filter(due_date__lt=now, notified=False).count()
        upcoming_tasks = tasks.filter(
            due_date__gt=now, 
            due_date__lt=now + timedelta(days=7)
        ).count()
        
        return {
            'tasks': task_data,
            'stats': {
                'total': total_tasks,
                'completed': completed_tasks,
                'overdue': overdue_tasks,
                'upcoming': upcoming_tasks
            }
        }
    
    def _get_assessment_analytics(self, start_date):
        top_sessions = (
            Assessments.objects.values('session_key__session_name', 'session_key__session_code')
            .annotate(
                avg_score=Avg('total_mark'),
                assessment_count=Count('id')
            )
            .filter(assessment_count__gte=1) 
            .order_by('-avg_score')[:5]
        )
        
        weekly_trends = (
            Assessments.objects.filter(created_on__gte=start_date)
            .annotate(week=F('created_on__week'))
            .values('week')
            .annotate(
                count=Count('id'),
                avg_mark=Avg('total_mark')
            )
            .order_by('week')
        )
        
        duration_stats = (
            Assessments.objects.annotate(
                duration_minutes=F('end_time__hour') * 60 + F('end_time__minute') - 
                                (F('start_time__hour') * 60 + F('start_time__minute'))
            )
            .aggregate(
                avg_duration=Avg('duration_minutes'),
                max_duration=Max('duration_minutes'),
                min_duration=Min('duration_minutes')
            )
        )
        
        return {
            'top_sessions': list(top_sessions),
            'weekly_trends': list(weekly_trends),
            'duration_stats': duration_stats
        }
    
    def _get_recent_sessions(self):
        recent_sessions = Session.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        serializer = SessionSerializer(recent_sessions, many=True)
        return serializer.data



class AssessmentTaskStatsView(APIView):
    """
    API view to get counts of assessments and tasks
    """
    def get(self, request):
        assessment_count = Assessments.objects.count()
        task_count = Tasks.objects.count()
        
        return Response({
            'assessments': assessment_count,
            'tasks': task_count
        }, status=status.HTTP_200_OK)