from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'individual-live-sessions', OneToOneLiveVideoViewSet, basename='individual-live-session')

urlpatterns = [
    path('', include(router.urls)),
    path('get-group-session/', GetScheduleSessionView.as_view()),
    path('schedule-group-session/', ScheduleAGroupVideoMeetingSessionView.as_view()),
    path('change-session-status/', ChangeStatusOfMeet.as_view()),
    
]