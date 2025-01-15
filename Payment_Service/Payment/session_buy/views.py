from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from django.shortcuts import redirect
import uuid
from .models import Subscription, Payment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
# print jwt token
class StripeCheckoutView(APIView):
    def post(self, request):
        try:
            print("REQUESt DAAT :",request.data)
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = int(request.data.get('amount'))*100  # Amount in cents (e.g., $10 = 1000)

            session_key = Subscription.objects.get(session_code=session_code, tutor_code=tutor_code)
            print("SESSIOn KEY :",session_key)
            print("AS :: AS", amount, tutor_code, session_code)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': session_name,
                            },
                            'unit_amount': amount,  # Amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"{settings.SITE_URL}/tutor/payment-success/",
                cancel_url=f"{settings.SITE_URL}/tutor/payment-cancel",
                metadata={
                    'user_id': request.user.id,
                    'session_name': session_name,
                    'tutor_code': tutor_code,
                    'session_code': session_code,
                },
            )
            print("AFTER SESSIOn :",checkout_session)
            
            # payment = Payment.objects.create(
            #     subscription_key=session_key,
            #     amount=amount / 100,
            #     transaction_id=checkout_session.payment_intent,
            #     status="success",
            # )
            # print("PAYMENT:", payment)
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
                }, status=status.HTTP_200_OK)
        except Exception as e:
            print("ERROR", e)
            return Response({
                "error": str(e),
                 }, status=status.HTTP_502_BAD_GATEWAY
            )

        
@csrf_exempt
def stripe_webhook(request):
    print("STRIPE WORK 1")
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    print("STRIPE WORK 2")
    try:
        
        print("STRIPE WORK 3")
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            
            print("STRIPE WORK 3")
            session = event['data']['object']
            session_id = session['id']
            payment_intent = session.get('payment_intent')

            if payment_intent:
                payment = stripe.PaymentIntent.retrieve(payment_intent)

                # Find the subscription (session_code, tutor_code) using metadata from the session
                tutor_code = session['metadata']['tutor_code']
                session_code = session['metadata']['session_code']
                amount = session['amount_total'] / 100  # Convert from cents to dollars

                session_key = Subscription.objects.get(session_code=session_code, tutor_code=tutor_code)

                # Now that the payment has been completed, create a Payment record
                Payment.objects.create(
                    subscription_key=session_key,
                    amount=amount,
                    transaction_id=payment_intent,
                    status="success",
                )

                print(f"Payment successful: {payment_intent}")

            else:
                print("Payment intent is not available.")

        return JsonResponse({'status': 'success'}, status=200)

    except ValueError as e:
        # Invalid payload
        print("Invalid payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Signature verification failed")
        return JsonResponse({'error': 'Signature verification failed'}, status=400)