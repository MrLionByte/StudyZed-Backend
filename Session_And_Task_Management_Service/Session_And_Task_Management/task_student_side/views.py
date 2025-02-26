
from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import *
from .serializers import *
from session_tutor.models import Session
from datetime import datetime
from django.utils.timezone import now
from .jwt_utils import decode_jwt_token
from rest_framework.exceptions import ValidationError
from session_tutor.producer import kafka_producer
# Create your views here.

    
class GetAllTasksForStudentView(generics.ListAPIView):
    serializer_class = TasksThisMonthSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        today = now()
        session_code = self.request.query_params.get('session_code')
        if not session_code:
            raise ValidationError("Session code is required.")
        return Tasks.objects.filter(
            due_date__year=today.year, 
            due_date__month=today.month,
            session__session_code = session_code
        ).order_by('due_date')


class AttendTasksView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")
        answer = request.data.get("answer")

        if not task_id or not answer:
            return Response(
                {"error": "Task ID and answer are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            user_data = decode_jwt_token(request)
            student_code = user_data["user_code"]
        except Exception as e:
            return Response(
                {"error": "Invalid or missing token.", "details": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            student = StudentsInSession.objects.get(student_code=student_code)
        except StudentsInSession.DoesNotExist:
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            task = Tasks.objects.get(id=task_id)
        except Tasks.DoesNotExist:
            return Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        existing_task = AssignedTask.objects.filter(student=student, task=task).first()
        if existing_task:
            return Response(
                {
                    "message": "Task already attended.",
                    "task_id": task.id,
                    "answer": existing_task.answer,
                },
                status=status.HTTP_200_OK,
            )
            
        assigned_task, created = AssignedTask.objects.get_or_create(student=student, task=task)
        assigned_task.answer = answer
        assigned_task.save()
        
        data = {
            'title': assigned_task.task.title,
            'tutor_code': assigned_task.task.session.tutor_code,
            'message': f"task: {assigned_task.task.title} submitted by student {student_code}",
            "type": "reminder" 
        }
        
        kafka_producer.producer_message('attended_task', student_code, data)
        
        return Response(
            {"message": "Task attended successfully.", "task_id": task_id, "answer": answer},
            status=status.HTTP_201_CREATED,
        )

