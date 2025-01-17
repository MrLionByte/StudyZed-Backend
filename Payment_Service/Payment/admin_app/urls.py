from .views import *
from django.urls import path

urlpatterns = [
    path("session-payment-details/", GetPaymentOfSessionView.as_view()),
]
