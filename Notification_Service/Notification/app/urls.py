from django.urls import path
from .views import TestNotification

urlpatterns = [
    path("test-notification/", TestNotification.as_view()),
]
