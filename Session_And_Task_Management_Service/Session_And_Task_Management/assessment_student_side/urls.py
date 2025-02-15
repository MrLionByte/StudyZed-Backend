from django.urls import path
from .views import * 


urlpatterns = [

    path('get-assessment-for-students/', GetAssessmentsForStudentViews.as_view()),
    path('attend-assessment/', AttendAssessmentViews.as_view()),
    
    path('all-attended-assessments/', GetAttendedAssessmentsView.as_view()),
    
]
