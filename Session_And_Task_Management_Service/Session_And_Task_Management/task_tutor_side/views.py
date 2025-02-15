from django.shortcuts import render
from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Tasks
from task_student_side.models import AssignedTask
from .serializers import TasksSerializer, AssignedTaskScoreSerializer
from session_tutor.models import Session
from datetime import datetime
# Create your views here.

class CreateNewTaskView(generics.CreateAPIView):
    serializer_class = TasksSerializer
    permission_classes = [AllowAny]
    queryset = Tasks.objects.all()
    
    def create(self, request, *args, **kwargs):
    
        try:
            print(request.data)
            title = request.data.get('title')
            description = request.data.get('description')
            session_code = request.data.get('session')
            due_date_and_time = request.data.get('date_and_time')
            print(session_code, due_date_and_time, description, title)
            session = Session.objects.get(session_code=session_code['session_code'])
            task = Tasks.objects.create(
                session=session,
                title=title, 
                description=description,
                due_date=due_date_and_time,
                )
            serializer = self.get_serializer(task)
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
        tasks = Tasks.objects.prefetch_related("attended__student").all()  
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)

            
class GiveMarkForDailyTaskView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
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