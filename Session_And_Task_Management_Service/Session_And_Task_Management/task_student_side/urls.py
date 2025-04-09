from django.urls import path
from .views import * 


urlpatterns = [

    path('get-tasks-for-students/', GetAllTasksForStudentView.as_view()),
    path('task-submit-answer/',AttendTasksView.as_view()),
    
]