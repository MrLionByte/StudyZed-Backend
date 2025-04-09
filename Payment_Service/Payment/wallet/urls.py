from .views import *
from django.urls import path

urlpatterns = [
    path('student-wallet/', StudentWalletView.as_view()),
    path('tutor-wallet/', TutorWalletView.as_view()),
    
    path('create-wallet-transaction/', StripeWalletTransactionView.as_view()),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook')
]
