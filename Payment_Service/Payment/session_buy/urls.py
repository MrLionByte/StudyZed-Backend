from .views import *
from django.urls import path

urlpatterns = [
    path('create-checkout-session/', StripeCheckoutView.as_view()),
    # path('stripe-webhook/', StripeWebHookView.as_view()),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    
    path('pay-using-wallet/', PayForSessionUsingWalletView.as_view()),
    
    path('subscription-delete/', DeleteSubscriptionView.as_view()),

]
