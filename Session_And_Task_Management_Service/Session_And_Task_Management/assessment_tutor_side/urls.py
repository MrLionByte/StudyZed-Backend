from django.urls import path
from .views import * 


urlpatterns = [

    path('create-assessment/', CreateAssessmentView.as_view()),
    path('add-question/', AddQuestionsToAssessmentView.as_view()),
    
    path('get-assessments/', GetAssessmentView.as_view()),
    path('attended-students/',AttendedStudentsAndMark.as_view()),
    path('attended-students/assessment/',AttendedAssessment.as_view()),
    
    path('attended-students/assessment/update-mark/'
         ,UpdateMarkForAssessmentView.as_view())
]
