from .views import *
from django.urls import path

urlpatterns = [
    path('create-checkout-session/', StripeCheckoutView.as_view()),
    
    path('stripe-webhook/', stripe_webhook)

]
