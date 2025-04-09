from django.urls import path
from .views import StudentsAssessmentPerformancePerMonthViews, StudentsDailyAssessmentPerformancePerMonthViews


urlpatterns = [
    path('assessment-performance-graph/', StudentsAssessmentPerformancePerMonthViews.as_view()),  
    path('daily-performance-graph/', StudentsDailyAssessmentPerformancePerMonthViews.as_view()),  
]
