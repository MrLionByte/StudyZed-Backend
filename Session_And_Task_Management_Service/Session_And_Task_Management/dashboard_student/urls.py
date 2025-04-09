from django.urls import path
from .views import *


urlpatterns = [
    path('data/', StudentDashboardDataView.as_view()),
    path('table-view/', StudentLeaderBoardAndTableView.as_view()),
    
]
