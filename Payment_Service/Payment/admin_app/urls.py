from .views import *
from django.urls import path

urlpatterns = [
    path("session-payment-details/", GetPaymentOfSessionView.as_view()),
    path('total-revenue/', TotalRevenueView.as_view(), name='total-revenue'),
]
