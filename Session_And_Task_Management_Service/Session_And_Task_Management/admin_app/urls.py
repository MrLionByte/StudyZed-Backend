from django.urls import path
from . import views


urlpatterns = [
    path("see-session-to-approve/", views.AllSessionToApproveView.as_view()),
    path("approve-session/<int:pk>/", views.ApproveSessionView.as_view()),
    path("see-session-active/", views.AllActiveSessionsView.as_view()),
    path("block-session/<int:pk>/", views.BlockASessionView.as_view()),
    path("see-blocked-session/", views.AllBlockedSessionsView.as_view()),
]
