from django.urls import path
from .views import * 


urlpatterns = [
    path('create-session/', CreateSessionView.as_view()),
    path('view-session/', GetSessionView.as_view()),
    
    path('tutor-sessions/', TutorsSessionsView.as_view()),
    
    path('all-session-students/', StudentsInSessionView.as_view()),
    path('approve-student-to-session/<int:pk>/', ApproveStudentToSessionView.as_view()),
    
]
