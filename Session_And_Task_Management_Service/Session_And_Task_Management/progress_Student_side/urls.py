from django.urls import path
from .views import *


urlpatterns = [
    path('assessment-performance-graph/', StudentPersonalAssessmentPerformanceView.as_view()),  
    path('daily-performance-graph/', StudentPersonalTaskPerformanceView.as_view()),  
]
