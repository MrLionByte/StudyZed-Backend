from django.shortcuts import render
from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Tasks
from task_student_side.models import AssignedTask
from .serializers import TasksSerializer, AssignedTaskScoreSerializer, TaskEditSerializer
from session_tutor.models import Session
from datetime import datetime
from django.utils import timezone
from session_tutor.producer import kafka_producer
from students_in_session.models import StudentsInSession
from django.core.serializers import serialize
from session_tutor.permissions import TutorAccessPermission
# Create your views here.

class CreateNewTaskView(generics.CreateAPIView):
    serializer_class = TasksSerializer
    permission_classes = [TutorAccessPermission]
    queryset = Tasks.objects.all()
    
    def create(self, request, *args, **kwargs):
    
        try:
           
            title = request.data.get('title')
            description = request.data.get('description')
            session_code = request.data.get('session')
            due_date_and_time = request.data.get('date_and_time')
           
            session = Session.objects.get(session_code=session_code['session_code'])
            task = Tasks.objects.create(
                session=session,
                title=title, 
                description=description,
                due_date=due_date_and_time,
                )
            
            serializer = self.get_serializer(task)
            student_codes = list(StudentsInSession.objects.filter(session=session).values_list('student_code', flat=True))
            
            data = {
                "message": f"you have daily task :{task.title} tomorrow",
                "task": {
                        "task": task.id,
                        "title": task.title,
                        "due_date": task.due_date,
                },
                "type": "reminder",
                "student_codes":student_codes
            }
            kafka_producer.producer_message('daily_task', session_code, data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print("ERROR TASK :", e)
            return
        
# class GetAllTasksView(generics.ListAPIView):
#     serializer_class = TasksSerializer
#     permission_classes = [AllowAny]
    
#     def get_queryset(self):
#         session_code = self.request.query_params.get('session_code', None)
#         return Tasks.objects.filter(
#             session__session_code=session_code
#         ).prefetch_related("attended__student")

class GetAllTasksView(APIView):
    def get(self, request):
        session_code = self.request.query_params.get('session_code')
        tasks = Tasks.objects.filter(
            session__session_code=session_code).prefetch_related(
                "attended__student").all()  
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)

class EditTaskView(generics.UpdateAPIView):
    permission_classes = [TutorAccessPermission]
    serializer_class = TaskEditSerializer
    queryset = Tasks.objects.filter(due_date__gte=timezone.now())
    lookup_field = 'id'
    lookup_url_kwarg = 'task_id'
    
    def update(self, request, *args, **kwargs):
        partial_update = kwargs.pop('partial', False)
        task_instance = self.get_object()
        
        serializer = self.get_serializer(
            task_instance, data=request.data, partial=partial_update)
        task_id = request.data.get('id')
        date = request.data.get('date')
        task = Tasks.objects.get(id=task_id)
        if task.due_date != date:
            task.due_date=date
            task.save()
            
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response( serializer.data, 
                status=status.HTTP_202_ACCEPTED)
       
class GiveMarkForDailyTaskView(generics.UpdateAPIView):
    permission_classes = [TutorAccessPermission]
    queryset = AssignedTask.objects.all()
    serializer_class = AssignedTaskScoreSerializer

    def update(self, request, *args, **kwargs):
        task_data = self.get_object()
        score = request.data.get('score')
        if score is None:
            raise ValidationError("Score is required.")
        try:
            score = int(score)
            if not (1 <= score <= 10):
                raise ValidationError("Score must be between 1 and 10.")
        except ValueError:
            raise ValidationError("Score must be a number.")

        task_data.score = score
        task_data.save()

        return Response({
            "id": task_data.id,
            "score": task_data.score,
        }, status=status.HTTP_202_ACCEPTED)

