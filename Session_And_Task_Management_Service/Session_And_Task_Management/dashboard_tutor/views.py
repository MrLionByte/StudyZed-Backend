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
from studymaterial.models import StudyMaterial
from session_tutor.utils.jwt_utils import decode_jwt_token
from session_tutor.permissions import TutorAccessPermission
# Create your views here.


class TutorDashboardDataView(views.APIView):
    permission_classes = [TutorAccessPermission]
    
    def get(self, request):
        
        session_code = request.query_params.get("session_code")
        print(request.data)
        print(session_code)
        
        no_of_students = StudentsInSession.objects.filter(
            session__session_code=session_code).count()
        
        no_of_study_materials = StudyMaterial.objects.filter(
            session_key=session_code
        ).count()
        
        total_assessments = Assessments.objects.filter(
            session_key__session_code=session_code
        ).count()

        total_tasks = Tasks.objects.filter(
            session__session_code=session_code
        ).count()

        attended_assessments = StudentAssessment.objects.filter(
            assessment__session_key__session_code = session_code,
            is_completed=True
        ).count()

        completed_tasks = AssignedTask.objects.filter(
            task__session__session_code=session_code
        ).count()

        late_submissions = StudentAssessment.objects.filter(
            is_late_submission=True,
            assessment__session_key__session_code = session_code
        ).count() + AssignedTask.objects.filter(
            is_late_submission=True,
            task__session__session_code=session_code
        ).count()

        total_scheduled = total_assessments + total_tasks
        total_completed = attended_assessments + completed_tasks
        completion_rate = (total_completed / total_scheduled) * 100 if total_scheduled > 0 else 0

        on_time_submissions = total_completed - late_submissions
        on_time_rate = (on_time_submissions / total_completed) * 100 if total_completed > 0 else 0

        return response.Response({
            "no_of_students": no_of_students,
            "no_of_materials": no_of_study_materials,
            "completion_rate": round(completion_rate, 2),
            "on_time_rate": round(on_time_rate, 2),
            "total_tasks_scheduled": total_tasks,
            "late_submission_count": late_submissions,       
        }, status=status.HTTP_200_OK)
        
class TutorLeaderBoardAndTableView(views.APIView):
    permission_classes = [TutorAccessPermission]
    
    def get(self, request):
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

        for score in assessment_scores:
            student_code = score["student_session__student_code"]
            leaderboard[student_code] = {
                "total_assessment_score": score["total_assessment_score"] or 0,
                "total_task_score": 0
            }

        for score in task_scores:
            student_code = score["student__student_code"]
            if student_code in leaderboard:
                leaderboard[student_code]["total_task_score"] = score["total_task_score"] or 0
            else:
                leaderboard[student_code] = {
                    "total_assessment_score": 0,
                    "total_task_score": score["total_task_score"] or 0
                }

        for student_code in leaderboard:
            leaderboard[student_code]["total_score"] = (
                leaderboard[student_code]["total_assessment_score"] +
                leaderboard[student_code]["total_task_score"]
            )

        leaderboard_list = sorted(
            leaderboard.items(), key=lambda x: x[1]["total_score"], reverse=True
        )

        latest_assessments = Assessments.objects.filter(
            session_key__session_code=session_code
        ).order_by("-start_time")[:3]
        
        top_assessments = []
        for assessment in latest_assessments:
            top_scorer = StudentAssessment.objects.filter(
                assessment=assessment
            ).order_by("-score").first()

            if top_scorer:
                top_assessments.append({
                    "assessment_title": assessment.assessment_title,
                    "top_scorer": top_scorer.student_session.student_code,
                    "score": top_scorer.score
                })

        latest_tasks = Tasks.objects.filter(
            session__session_code=session_code
        ).order_by("-due_date")

        top_tasks = []
        
        for task in latest_tasks:
            top_scorer = AssignedTask.objects.filter(
                task=task
            ).order_by("-score").first()

            if top_scorer:
                top_tasks.append({
                    "task_title": task.title,
                    "top_scorer": top_scorer.student.student_code,
                    "score": top_scorer.score
                })

        return response.Response({
            "leaderboard": leaderboard_list,
            "recent_assessments": top_assessments,
            "recent_tasks": top_tasks
        })
        