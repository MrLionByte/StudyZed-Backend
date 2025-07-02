from .views import (
    StripeWalletTransactionView,
    StudentWalletView,
    TutorWalletView,
    stripe_webhook_wallet
    )
from django.urls import path


urlpatterns = [
    path('student-wallet/', StudentWalletView.as_view()),
    path('tutor-wallet/', TutorWalletView.as_view()),
    
    path('create-wallet-transaction/', StripeWalletTransactionView.as_view()),
    path('stripe-webhook-wallet/', stripe_webhook_wallet, name='stripe_webhook_wallet')
]
