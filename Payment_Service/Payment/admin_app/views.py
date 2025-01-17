from rest_framework import generics
from .serializers import AdminSessionPaymentViewSerializer
from session_buy.models import Subscription
from rest_framework.exceptions import NotFound

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
    