from rest_framework import generics
from .serializers import AdminSessionPaymentViewSerializer
from session_buy.models import Subscription,Payment
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
# Create your views here.


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