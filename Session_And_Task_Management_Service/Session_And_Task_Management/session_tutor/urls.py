from django.urls import path
from .views import CreateSessionView, GetSessionView


urlpatterns = [
    path('create-session/', CreateSessionView.as_view()),
    path('view-session/', GetSessionView.as_view())
    
]
