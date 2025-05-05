import logging
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification, UserFCMToken
import json
from .serializer import NotificationSerializer
# Create your views here.

logger = logging.getLogger(__name__)

class TestNotification(APIView):
    def post(self, request):
        data = request.data
        logger.info('Test Data', extra={'data': data})
        return None

class SaveFCMTokenAndAuthorize(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_code = data.get("user_code")
            fcm_token = data.get("token")

            if not user_code or not fcm_token:
                return Response(
                    {"error": "Missing user_code or token"}, 
                    status=400
                    )
            token = UserFCMToken.objects(user_code=user_code).first()
            if not token or not token.fcm_token:
                UserFCMToken.objects(user_code=user_code).update_one(
                        set__fcm_token=fcm_token, upsert=True
                )
            return Response({"message": "FCM token saved successfully!"},
                            status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
class GetAllUnreadNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get(self, request, user_code, *args, **kwargs):
        notifications = Notification.objects.filter(
            user_code=user_code, is_read=False).order_by(
                '-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        user_code = self.kwargs.get("user_code")
        return Notification.objects.filter(
            user_code=user_code,
            is_read=False
        ).order_by('-created_at')
        
class MarkNotificationAsReadView(APIView):
    def post(self, request, *args, **kwargs):
        notification_id = request.data.get("notification_id")
        user_code = request.data.get("user_code")
        if not notification_id or not user_code:
            return Response({"error": "Missing notification_id or user_code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = Notification.objects(id=notification_id, user_code=user_code).first()
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception('Error', extra={'data': str(e)})
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    