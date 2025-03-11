from django.shortcuts import render
from rest_framework import status, response, generics, views
from rest_framework.permissions import AllowAny
from django.utils.timezone import now, timedelta
from django.db.models import Count, Avg, Q, Sum
from session_tutor.models import Session
from students_in_session.models import StudentsInSession
from assessment_tutor_side.models import Assessments
from assessment_student_side.models import StudentAssessment
from task_student_side.models import AssignedTask,Tasks
from session_tutor.utils.jwt_utils import decode_jwt_token
from students_in_session.permissions import StudentAccessPermission
# Create your views here.


class StudentDashboardDataView(views.APIView):
    permission_class = [StudentAccessPermission]
    
    def get(self, request):
        
        session_code = request.query_params.get("session_code")
        user_data = decode_jwt_token(request)
        print(request.data)
        print(session_code)
        today = now().date()
        # start_week = today - timedelta(days=today.weekday()) 
        # end_week = start_week + timedelta(days=6)  
        start_week = today - timedelta(days=6)  
        end_week = today 

        total_assessments = Assessments.objects.filter(
            session_key__session_code=session_code,
             start_time__date__range=(start_week, end_week)
        ).count()

        total_tasks = Tasks.objects.filter(
            session__session_code=session_code,
            due_date__date__range=(start_week, end_week)
        ).count()

        attended_assessments = StudentAssessment.objects.filter(
            student_session__student_code=user_data['user_code'],
            assessment__start_time__date__range=(start_week, end_week),
            is_completed=True
        ).count()

        completed_tasks = AssignedTask.objects.filter(
            student__student_code=user_data['user_code'],
            task__due_date__date__range=(start_week, end_week)
        ).count()

        late_submissions = StudentAssessment.objects.filter(
            student_session__student_code=user_data['user_code'],
            is_late_submission=True
        ).count() + AssignedTask.objects.filter(
            student__student_code=user_data['user_code'],
            is_late_submission=True
        ).count()

        total_scheduled = total_assessments + total_tasks
        total_completed = attended_assessments + completed_tasks
        
        performance = (total_scheduled/total_completed*100) if total_completed != 0 else 0
        print(total_scheduled, total_completed)
        completion_rate = (total_completed / total_scheduled) * 100 if total_scheduled > 0 else 0

        on_time_submissions = total_completed - late_submissions
        on_time_rate = (on_time_submissions / total_completed) * 100 if total_completed > 0 else 0

        avg_score = (
            StudentAssessment.objects.filter(student_session__student_code=user_data['user_code'])
            .aggregate(avg_score=Avg("score"))["avg_score"] or 0
        ) + (
            AssignedTask.objects.filter(student__student_code=user_data['user_code'])
            .aggregate(avg_score=Avg("score"))["avg_score"] or 0
        )

        return response.Response({
            "completion_rate": round(completion_rate, 2),
            "on_time_rate": round(on_time_rate, 2),
            "average_score": round(avg_score, 2),
            "total_tasks_scheduled": total_tasks,
            "late_submission_count": late_submissions,
            'performance': performance           
        }, status=status.HTTP_200_OK)
        

class StudentLeaderBoardAndTableView(views.APIView):
    permission_classes = [StudentAccessPermission]
    
    def get(self, request):
        user_data = decode_jwt_token(request)
        session_code = request.query_params.get("session_code")

        session_code = request.query_params.get("session_code")

        student_sessions = StudentsInSession.objects.filter(session__session_code=session_code)
        student_codes = student_sessions.values_list("student_code", flat=True)

        assessment_scores = StudentAssessment.objects.filter(
            student_session__student_code__in=student_codes
        ).values("student_session__student_code").annotate(
            total_assessment_score=Sum("score")
        )

        task_scores = AssignedTask.objects.filter(
            student__student_code__in=student_codes
        ).values("student__student_code").annotate(
            total_task_score=Sum("score")
        )

        leaderboard = {}

        for entry in assessment_scores:
            student_code = entry["student_session__student_code"]
            leaderboard[student_code] = {
                "total_assessment_score": entry["total_assessment_score"] or 0,
                "total_task_score": 0  
            }
            
        for entry in task_scores:
            student_code = entry["student__student_code"]
            if student_code in leaderboard:
                leaderboard[student_code]["total_task_score"] = entry["total_task_score"] or 0
            else:
                leaderboard[student_code] = {
                    "total_assessment_score": 0, 
                    "total_task_score": entry["total_task_score"] or 0
                }

        for student_code in leaderboard:
            leaderboard[student_code]["total_score"] = (
                leaderboard[student_code]["total_assessment_score"] +
                leaderboard[student_code]["total_task_score"]
            )

        leaderboard_list = sorted(
            leaderboard.items(), key=lambda x: x[1]["total_score"], reverse=True
        )

        recent_assessments = StudentAssessment.objects.filter(
            student_session__student_code=user_data['user_code'],
            student_session__session__session_code=session_code
        ).order_by("-started_on")[:3].values("assessment__assessment_title", "score")

        recent_tasks = AssignedTask.objects.filter(
            student__student_code=user_data['user_code'],
            task__session__session_code=session_code
        ).order_by("-completed_on")[:3].values("task__title", "score")

        return response.Response({
            "leaderboard": leaderboard_list,
            "recent_assessments": list(recent_assessments),
            "recent_tasks": list(recent_tasks)
        })
