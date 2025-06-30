from django.urls import path
from .views import * 


urlpatterns = [
    path('create-session/', CreateSessionView.as_view()),
    path('view-session/', GetSessionView.as_view()),
    path('update-session/', UpdateSessionViews.as_view()),
    
    path('tutor-sessions/', TutorsSessionsView.as_view()),
    
    path('all-session-students/', StudentsInSessionView.as_view()),
    path('approve-student-to-session/<int:pk>/', ApproveStudentToSessionView.as_view()),
    
    path('students-in-session/', StudentsDataInSessionView.as_view()),

    path("delete/", DeleteSessionView.as_view()),

]
