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
from django.views.decorators.http import require_POST
from django.conf import settings
from wallet.models import WalletTransactions, Wallet
from decimal import Decimal
from rest_framework.permissions import AllowAny

stripe.api_key = settings.STRIPE_SECRET_KEY
# print jwt token
class StripeCheckoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = Decimal(request.data.get('amount'))*100  # Amount in cents (e.g., $10 = 1000)

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


class StripeWebHookView(APIView):
    def post(self, request):
        print("Working StripeWebHook")
        return JsonResponse({"OK":"OK"})

  
@csrf_exempt
@require_POST
def stripe_webhook(request):
    print("STRIPE WORK 1")
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_SESSION

    print("STRIPE WORK 2", endpoint_secret)
    try:
        
        print("STRIPE WORK 3")
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'checkout.session.completed':
            
            print("STRIPE WORK 3")
            session = event['data']['object']
            print("SESSion :" ,session)
            session_id = session['id']
            payment_intent = session.get('payment_intent')

            if payment_intent:
                payment = stripe.PaymentIntent.retrieve(payment_intent)

                tutor_code = session.get('metadata', {}).get('user_code') or session.get('metadata', {}).get('tutor_code')

                session_code = session['metadata']['session_code']
                amount = session['amount_total'] / 100  # Convert from cents to dollars

                session_key = Subscription.objects.get(session_code=session_code, tutor_code=tutor_code)

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
        print("Invalid payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    except stripe.error.SignatureVerificationError as e:
        print("Signature verification failed")
        return JsonResponse({'error': 'Signature verification failed'}, status=400)
    
    
class PayForSessionUsingWalletView(APIView):
    # permission_classes = [TutorAccessPermission]
    
    def post(self, request):
        try:
            print("REQUESt DAAT :",request.data)
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = int(request.data.get('amount'))  # Amount in cents (e.g., $10 = 1000)

            
            wallet, created = Wallet.objects.get_or_create(user_code=tutor_code);
            print(wallet, "::",amount, "::",wallet.balance)
            if wallet.balance < amount:
                return Response({
                "payment-status": "insufficient-balance"
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

            wallet_transaction = WalletTransactions.objects.create(
                wallet_key=wallet,
                transaction_type="DEBIT",
                amount=amount,
                status="Pending"
            )
            print("SUB :",tutor_code, session_code)
            session_key = Subscription.objects.get(session_code=session_code, tutor_code=tutor_code)
            print("SES K :", session_key)
            subscription_payment = Payment.objects.create(
                    subscription_key=session_key,
                    amount=amount,
                    status="success",
                )
            
            if subscription_payment.status == 'success':
                wallet_transaction.status = "Completed"
            elif subscription_payment.status == 'failed':
                wallet_transaction.status = "Failed"
            wallet_transaction.save()

            return Response({
                "payment": subscription_payment,
                "payment-status": "success"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(e)
            return Response({
                "error": str(e),
                "payment-status": "failed"
                } 
            ,status=status.HTTP_400_BAD_REQUEST)
            