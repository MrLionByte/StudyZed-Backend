# from django.shortcuts import render
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from .serializers import PaymentSerializer, SubscriptionSerializer
# from .models import Payment, Subscription
# # Create your views here.


# class SubscriptionView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = SubscriptionSerializer
#     queryset = Subscription.objects.all()
    

# class PaymentView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = PaymentSerializer
#     queryset = Payment.objects.all()
    
#     def perform_create(self, serializer):
#         subscription_key = serializer.validated_data.get('subscription_key')
#         print(subscription_key)
#         serializer.save()
#         # if subscription_key.is_expired():
#         #     serializer.save()
#         # else:
#         #     serializer.save()

