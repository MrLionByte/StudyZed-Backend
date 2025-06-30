import logging
import requests
from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from django.shortcuts import redirect,get_object_or_404
import uuid
from .models import Subscription, Payment
from .utils.jwt_utils import decode_jwt_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from wallet.models import WalletTransactions, Wallet
from decimal import Decimal
from rest_framework.permissions import AllowAny
from wallet.permissions import TutorAccessPermission
from .serializers import PaymentSerializer
from decimal import Decimal 

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

SESSION_SERVICE_URL = "http://session-and-task-service:8009/session-tutor/delete/"

class StripeCheckoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = Decimal(request.data.get('amount'))*100  # Amount in cents (e.g., $10 = 1000)
            
            import urllib.parse
            encoded_session_code = urllib.parse.quote_plus(session_code)

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
                cancel_url=f"{settings.SITE_URL}/tutor/payment-cancel?session_code={encoded_session_code}",
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
            logger.error("ERROR", extra={'data': str(e)})
            return Response({
                "error": str(e),
                 }, status=status.HTTP_502_BAD_GATEWAY
            )


class StripeWebHookView(APIView):
    def post(self, request):
        return JsonResponse({"OK":"OK"})

  
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_SESSION

    try:       
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'checkout.session.completed':
            print("Payment Working Fine")
            session = event['data']['object']
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

            else:
                logger.warning("Payment intent is not available.")

        if event['type'] in ['checkout.session.expired', 'checkout.session.async_payment_failed']:
            deleted=Subscription.objects.filter(session_code=session_code, tutor_code=tutor_code).delete()
            print(f'Stripe Failed : {deleted}')
            try:
                delete_url = f"{SESSION_SERVICE_URL}{session_code}/"
                print(f'Deleted url : {delete_url}')
                headers = {
                    "X-Delete-Secret": settings.SESSION_DELETE_SECRET
                }
                response = requests.delete(delete_url, headers=headers, timeout=5)
                response.raise_for_status()
                print('Delete output ', response)
                logger.info(f"Session {session_code} deleted from Session Service")
            except Exception as e:
                logger.error(f"Failed to delete session {session_code} from Session Service: {str(e)}")

        return JsonResponse({'status': 'success'}, status=200)

    except ValueError as e:
        logger.warning("Invalid payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    except stripe.error.SignatureVerificationError as e:
        logger.error("Signature verification failed", extra={'data': str(e)})
        return JsonResponse({'error': 'Signature verification failed'}, status=400)
    
    
class PayForSessionUsingWalletView(APIView):
    permission_classes = [TutorAccessPermission]
    
    def post(self, request):
        try:
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = int(request.data.get('amount'))

            wallet, created = Wallet.objects.get_or_create(user_code=tutor_code);
            
            if wallet.balance < amount:
                logger.warning(f"Insufficient balance for tutor {tutor_code} to pay for session {session_code}. Required: {amount}, Available: {wallet.balance}")
                return Response({
                "payment-status": "insufficient-balance"
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            subscription_instance = get_object_or_404(Subscription, session_code=session_code, tutor_code=tutor_code)

            wallet_transaction = WalletTransactions.objects.create(
                wallet_key=wallet,
                transaction_type="DEBIT",
                amount=amount,
                status="Pending"
            )
            
            subscription_payment = Payment.objects.create(
                    subscription_key=subscription_instance,
                    amount=amount,
                    status="success",
                    transaction_id=wallet_transaction.wallet_transaction_id
                )
            
            if subscription_payment.status == 'success':
                wallet_transaction.status = "Completed"
            elif subscription_payment.status == 'failed':
                wallet_transaction.status = "Failed"
            wallet_transaction.save()
            
            serialized_payment_data = PaymentSerializer(subscription_payment).data

            return Response({
                "payment": serialized_payment_data,
                "payment-status": "success"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception("Error occured", extra={'data': str(e)})
            return Response({
                "error": str(e),
                "payment-status": "failed"
                } 
            ,status=status.HTTP_400_BAD_REQUEST)


class DeleteSubscriptionView(APIView):
    permission_classes = [TutorAccessPermission]
    
    def delete(self, request):
        session_code = request.data.get('session_code')
        user_data = decode_jwt_token(self.request)
        tutor_code = user_data.get("user_code")
        
        deleted, _ = Subscription.objects.filter(
            session_code=session_code,
            tutor_code=tutor_code
            ).delete()
        print("In deletion :",deleted)
        
        if deleted:
            return Response({"message": "Subscription deleted."}, status=status.HTTP_200_OK)
        return Response({"error": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)

