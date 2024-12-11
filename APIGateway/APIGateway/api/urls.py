from django.urls import path
from .views import APIgateView

urlpatterns = [
    
    path('auth-app/', APIgateView.as_view(), name='api_gateway'),

]
