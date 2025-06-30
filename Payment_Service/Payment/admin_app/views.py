import logging
from rest_framework import generics
from .serializers import AdminSessionPaymentViewSerializer
from session_buy.models import Subscription,Payment
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db import transaction
from decimal import Decimal

logger = logging.getLogger(__name__)

from wallet.models import Wallet, WalletTransactions
# Create your views here.

class TestAPIRequestView(APIView):
    def get(self, request):
        logger.debug(f"Request headers: {request.META}")
        print(f"Request Working : {request}")
        return Response({"message": "received request"}, status=status.HTTP_200_OK)


class GetPaymentOfSessionView(generics.ListAPIView):
    serializer_class = AdminSessionPaymentViewSerializer
    
    def get_queryset(self):
        session_code = self.request.query_params.get("session_code")
        tutor_code = self.request.query_params.get("tutor_code")
        if not session_code:
            raise NotFound(detail="session_code is required.")
        if not tutor_code:
            raise NotFound(detail="tutor_code is required.")

        return Subscription.objects.filter(
            session_code=session_code,
            tutor_code=tutor_code
        ).prefetch_related("payment_set")
        
        
class RejectSessionPaymentRefund(APIView):
    def post(self, request):
        print("Working Refund")
        session_code = request.data.get("session_code")
        tutor_code = request.data.get("tutor_code")
        print("CODE :", session_code, tutor_code)
        
        if not session_code or not tutor_code:
            return Response({"error": "Missing session_code or tutor_code"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            subscription = Subscription.objects.get(
                session_code=session_code,
                tutor_code=tutor_code
                )
            print(f"1 : {subscription}")
        except Subscription.DoesNotExist:
            return Response(
                {"error": "Subscription not found"},
                status=status.HTTP_404_NOT_FOUND)

        try:
            payment = Payment.objects.get(
                subscription_key=subscription
                )
            print(f"2 : {payment}")
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND)

        try:
            wallet = Wallet.objects.get(
                user_code=tutor_code)
            print(f"3 : {wallet}")
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            subscription.is_active = False
            subscription.save()

            payment.status = "refunded"
            payment.save()
            
            print(f"4 : {payment}")
            
            WalletTransactions.objects.create(
                wallet_key=wallet,
                transaction_type="CREDIT",
                amount=payment.amount,
                note=f"Refund for session {session_code}",
                status="COMPLETED",
                currency=wallet.currency_mode
            )
            print(f"5 : Successful")
            

        return Response({"message": "Refund completed"}, status=status.HTTP_200_OK)




class TotalRevenueView(APIView):
    """
    API endpoint to get the total revenue from successful payments
    """
    def get(self, request):
        total_revenue = Payment.objects.filter(
            status="success"
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_revenue': total_revenue
        }, status=status.HTTP_200_OK)