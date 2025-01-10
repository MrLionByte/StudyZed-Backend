from .views import *
from django.urls import path

urlpatterns = [
    path('student-wallet/', StudentWalletView.as_view())
]
