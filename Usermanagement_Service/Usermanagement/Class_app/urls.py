from django.urls import path
from .views import *


urlpatterns = [
    # path("session-student-details/", StudentDetailsView.as_view()),
    
    path("session-student-details/", AllStudentsInAClassView.as_view()),
    path("tutor-session-details/", TutorOfSessionDetailsView.as_view()),
    
]
