from django.urls import path
from .views import *


urlpatterns = [
    path('data/', TutorDashboardDataView.as_view()),
    path('table-view/', TutorLeaderBoardAndTableView.as_view()),
    
]
