from celery import shared_task
from .models import Notification, UserFCMToken
from datetime import datetime,timedelta
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from confluent_kafka import Consumer
import json
import pytz
import requests
from django.db.models import Q
from mongoengine.queryset.visitor import Q as MongoQ
from firebase_admin import messaging
from app.firebase import send_firebase_notification

from django.core.exceptions import AppRegistryNotReady

def get_django_models():
    try:
        from .models import Notification, UserFCMToken
        return Notification, UserFCMToken
    except AppRegistryNotReady:
        return None, None

@shared_task
def test_notify():
    print("Notification Sent!")
    return "Success"

@shared_task
def send_notification():
    notifications = Notification.objects(is_read=False, notified=False)
    
    for notification in notifications:
        if notification.due_date and notification.type == "reminder":
            continue
        user_token = get_user_firebase_token(notification.user_code)
        
        if user_token:
            
            extra_data = {
                "due_time": str(notification.due_time) if notification.due_time else "0",
                "type": notification.type or ""
            }
            success, response = send_firebase_notification(
                registration_id=user_token,
                title=notification.title,
                body=notification.message,
                extra_data=extra_data
            )

            if success:
                notification.update(set__notified=True)
                print(f"Notification sent to {notification.user_code}: {response}")
            else:
                print(f"Failed to send notification: {response}")

    return "Unread notifications processed."

def get_user_firebase_token(user_code):
    user = UserFCMToken.objects(user_code=user_code).first()
    return user.fcm_token if user else None