import logging
import requests
from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Payment
from django.shortcuts import redirect,get_object_or_404
import uuid
from .models import Subscription, Payment
from wallet.models import Wallet, WalletTransactions
from .utils.jwt_utils import decode_jwt_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from wallet.models import WalletTransactions, Wallet
from decimal import Decimal
from django.db.models import F
from rest_framework.permissions import AllowAny
from wallet.permissions import TutorAccessPermission
from .serializers import PaymentSerializer

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
                    'type': 'session',
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
            
  
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_SESSION
        )
    except stripe.error.SignatureVerificationError:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_WALLET
            )
        except Exception as e:
            logger.error("Stripe signature verification failed for both secrets", extra={"data": str(e)})
            return JsonResponse({'error': 'Signature verification failed'}, status=400)

    try:
        event_type = event['type']

        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            payment_intent_id = session.get('payment_intent')
            amount = session.get('amount_total', 0) / 100  # Stripe sends amount in cents

            if payment_intent_id:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if metadata.get('type') == 'wallet':
                user_code = metadata.get('user_code')
                currency = metadata.get('currency', 'INR')

                try:
                    with transaction.atomic():
                        wallet = Wallet.objects.select_for_update().get(user_code=user_code)
                        WalletTransactions.objects.create(
                            wallet_key=wallet,
                            transaction_type="CREDIT",
                            amount=Decimal(amount),
                            transaction_id=session['id'],
                            currency=currency,
                            status="COMPLETED"
                        )

                        wallet.balance = F('balance') + Decimal(amount)
                        wallet.save()
                        
                    logger.info(f"Wallet top-up successful: {payment_intent_id}")

                except Wallet.DoesNotExist:
                    logger.error(f"Wallet not found for user_code: {user_code}")
                    return JsonResponse({'error': 'Wallet not found'}, status=404)

            elif metadata.get('type') == 'session':
                tutor_code = metadata.get('tutor_code')
                session_code = metadata.get('session_code')

                try:
                    session_key = Subscription.objects.get(session_code=session_code, tutor_code=tutor_code)

                    Payment.objects.create(
                        subscription_key=session_key,
                        amount=Decimal(amount),
                        transaction_id=payment_intent_id,
                        status="success",
                    )

                    logger.info(f"Session payment successful: {payment_intent_id}")

                except Subscription.DoesNotExist:
                    logger.error(f"Subscription not found for session_code: {session_code}")
                    return JsonResponse({'error': 'Subscription not found'}, status=404)

        elif event_type in ['checkout.session.expired', 'checkout.session.async_payment_failed']:
            metadata = event['data']['object'].get('metadata', {})
            if metadata.get("type") == "session":
                tutor_code = metadata.get("tutor_code")
                session_code = metadata.get("session_code")

                Subscription.objects.filter(session_code=session_code, tutor_code=tutor_code).delete()

                try:
                    delete_url = f"{settings.SESSION_SERVICE_URL}{session_code}/"
                    headers = {"X-Delete-Secret": settings.SESSION_DELETE_SECRET}
                    requests.delete(delete_url, headers=headers, timeout=5)
                    logger.info(f"Deleted session on failure: {session_code}")
                except Exception as e:
                    logger.error(f"Failed to delete session: {str(e)}")

        return JsonResponse({'status': 'success'}, status=200)

    except Exception as e:
        logger.exception("Unhandled Stripe webhook error", extra={"data": str(e)})
        return JsonResponse({'error': str(e)}, status=400)
    
    
class PayForSessionUsingWalletView(APIView):
    permission_classes = [TutorAccessPermission]
    
    @transaction.atomic
    def post(self, request):
        try:
            session_name = request.data.get('session_name')
            tutor_code = request.data.get('tutor_code')
            session_code = request.data.get('session_code')
            amount = Decimal(str(request.data.get('amount')))

            subscription_instance = get_object_or_404(
                Subscription, session_code=session_code, tutor_code=tutor_code
                )

            wallet, _ = Wallet.objects.get_or_create(user_code=tutor_code);
            
            if wallet.balance < amount:
                logger.warning(
                    f"Insufficient balance for tutor {tutor_code}. Required: {amount}, Available: {wallet.balance}"
                )
                return Response(
                    {"payment-status": "insufficient-balance"},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
            
            wallet.balance -= amount
            wallet.save()
            
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
            
            serialized_payment_data = PaymentSerializer(subscription_payment).data

            return Response({
                "payment": serialized_payment_data,
                "payment-status": "success"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception("Payment failed", extra={'data': str(e)})
            return Response({
                "error": str(e),
                "payment-status": "failed"
            }, status=status.HTTP_400_BAD_REQUEST)


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
        
        if deleted:
            return Response({"message": "Subscription deleted."}, status=status.HTTP_200_OK)
        return Response({"error": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)

