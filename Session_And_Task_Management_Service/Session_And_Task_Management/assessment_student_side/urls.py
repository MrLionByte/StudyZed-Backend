from django.urls import path
from .views import * 


urlpatterns = [

    path('get-session-for-students/', GetAssessmentsForStudentViews.as_view()),
    
]
