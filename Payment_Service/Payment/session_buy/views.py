from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
import uuid

stripe.api_key = settings

class CreateCheckoutSession(APIView):
  def post(self, request):
    data = request.data
    try:
        price = data.get('price')
        product_name = data.get('product_name')
        
        checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',  # Change to your currency
                            'product_data': {
                                'name': product_name,
                            },
                            'unit_amount': int(float(price) * 100),  # Stripe expects amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/payment-success') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/payment-cancel'),
        )
        Payment.objects.create(
                payment_id=uuid.uuid4(),
                subscription_key_id=data.get('subscription_key'),
                amount=price,
                transaction_id=checkout_session.id,
                status='pending'
            )
        