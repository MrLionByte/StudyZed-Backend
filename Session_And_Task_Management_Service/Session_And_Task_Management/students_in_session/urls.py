from django.urls import path
from .views import *


urlpatterns = [
    path('enter-session/', StudentEnterSessionView.as_view()),
    path('view-session/', StudentSessionView.as_view()),
    
]
