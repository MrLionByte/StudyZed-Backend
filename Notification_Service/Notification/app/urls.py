from django.urls import path
from .views import TestNotification, SaveFCMTokenAndAuthorize, GetAllUnreadNotificationsView, MarkNotificationAsReadView

urlpatterns = [
    path("test-notification/", TestNotification.as_view()),
    path("save-fcm-token/", SaveFCMTokenAndAuthorize.as_view()),
    path("list/<str:user_code>/", GetAllUnreadNotificationsView.as_view()),
    path("mark-as-read/", MarkNotificationAsReadView.as_view()),
]
