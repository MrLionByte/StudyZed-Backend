import logging
from django.shortcuts import render
from django.db import transaction, IntegrityError

from .models import Wallet, WalletTransactions
from rest_framework import generics, status, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Prefetch, Subquery
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .permissions import StudentAccessPermission, TutorAccessPermission
from .jwt_utils import decode_jwt_token


stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

# Create your views here.


class WalletTransactionPagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 45


# STUDENT {

class StudentWalletView(generics.RetrieveAPIView):
    serializer_class = WalletViewSerializer
    permission_classes = [StudentAccessPermission]
    lookup_field = 'user_code'
   
    def get(self, request, *args, **kwargs):
        user_code = "DESIR-087C3A7"
        wallet = get_object_or_404(Wallet, user_code=user_code)
        
        # After applying pagination
        paginator = WalletTransactionPagination()
        result_page = paginator.paginate_queryset(wallet_transactions, request)
        
        wallet_transactions = WalletTransactions.objects.filter(
            wallet_key=wallet).order_by('-transaction_date')[:9]
        wallet_data = self.get_serializer(wallet).data
        transactions_data = WalletTransactionsViewSerializer(
            result_page, many=True
        ).data
        
        wallet_data['transactions'] = transactions_data

        return paginator.get_paginated_response(wallet_data)

class StudentAddToWalletView(generics.CreateAPIView):
    pass


#  }

# TUTOR {

class TutorWalletView(generics.RetrieveAPIView):
    serializer_class = WalletViewSerializer
    permission_classes = [TutorAccessPermission]
    lookup_field = 'user_code'
   
    def get(self, request, *args, **kwargs):
        user_data = decode_jwt_token(self.request)
        user_code = user_data.get("user_code")
        wallet, created = Wallet.objects.get_or_create(user_code=user_code)
        
        wallet_transactions = WalletTransactions.objects.filter(
            wallet_key=wallet).order_by('-transaction_date')
        
        # After applying pagination
        paginator = WalletTransactionPagination()
        result_page = paginator.paginate_queryset(wallet_transactions, request)
        
        wallet_data = self.get_serializer(wallet).data
        transactions_data = WalletTransactionsViewSerializer(
            result_page, many=True
        ).data
        wallet_data['transactions'] = transactions_data

        return paginator.get_paginated_response(wallet_data)

#  }


class StripeWalletTransactionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            account_no = request.data.get('account_number')
            user_code = request.data.get('user_code')
            url = request.data.get("url")
            amount = int(request.data.get('amount'))*100  # Amount in cents (e.g., $10 = 1000)
            currency = request.data.get('currency', 'inr')
            checkout_transaction = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': user_code,
                            },
                            'unit_amount': amount,  # Amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"{url}?transaction_id={user_code}&status=success",
                cancel_url=f"{url}?transaction_id={user_code}&status=cancel",
                metadata={
                    'type': 'wallet',
                    'account_no': account_no,
                    'user_code': user_code,
                    'currency': currency,
                },
            )
            
            return Response({
                'checkout_url': checkout_transaction.url,
                'transaction_id': checkout_transaction.id
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Exception on transaction", extra={'data': str(e)})
            return Response({
                "error": str(e),
                 }, status=status.HTTP_502_BAD_GATEWAY
            )

  
@csrf_exempt
@require_POST
def stripe_webhook_wallet(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_WALLET

    try:

        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get("metadata", {})
            
            if metadata.get("type") != "wallet":
                logger.info("Non-wallet Stripe webhook received; ignored.")
                return JsonResponse({'status': 'ignored'}, status=200)
            
            user_code = metadata.get("user_code")
          
            session_id = session['id']
            payment_intent = session.get('payment_intent')
            
            try:
                wallet_key = Wallet.objects.get(user_code=user_code)
            except Wallet.DoesNotExist:
                logger.warning(f"Wallet not found for user_code: {user_code}")
                return JsonResponse({'status': 'wallet_not_found'}, status=400)

            if payment_intent:
                payment = stripe.PaymentIntent.retrieve(payment_intent)
                user_code = session['metadata']['user_code']

                currency = session['metadata'].get('currency', 'inr')
                amount = session['amount_total'] / 100  # Convert from cents to dollars
                
                try:
                    with transaction.atomic():
                        if WalletTransactions.objects.select_for_update().filter(transaction_id=session_id).exists():
                            logger.info(f"Duplicate transaction detected: {session_id}")
                            return JsonResponse({'status': 'duplicate_ignored'}, status=200)
                
                        WalletTransactions.objects.create(
                            wallet_key=wallet_key,
                            transaction_type="CREDIT",
                            amount=amount,
                            transaction_id=session_id,
                            currency=currency,
                            status="COMPLETED"
                        )
                        logger.info(f"Payment successful: {payment_intent}")
                except IntegrityError as e:
                    logger.warning(f"IntegrityError: Possibly duplicate transaction: {session_id}")
                    return JsonResponse({'status': 'duplicate_handled'}, status=200)
            
            else:
                logger.warning("Payment intent is not available.")

        return JsonResponse({'status': 'success'}, status=200)

    except ValueError as e:
        logger.error("Invalid payload", extra={'data': str(e)})
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    except stripe.error.SignatureVerificationError as e:
        logger.error("Signature verification failed", extra={'data': str(e)})
        return JsonResponse({'error': 'Signature verification failed'}, status=400)
    
    except Exception as e:
        logger.exception("Error processing webhook", extra={'data': str(e)})
        return JsonResponse({'error': str(e)}, status=400)