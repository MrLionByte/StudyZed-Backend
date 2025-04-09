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

def get_user_firebase_token(user_code):
    user = UserFCMToken.objects(user_code=user_code).first()
    return user.fcm_token if user else None

@shared_task(name="app.tasks.send_notification")
def send_notification():
    """Process all pending notifications in batch"""
    
    notifications = Notification.objects(notified=False)
    
    for notification in notifications:
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

@shared_task(name="app.tasks.send_notification_for_user")
def send_notification_for_user(user_code, title, body):
    """
    This can be called immediately after a notification is created, 
    Send immediate notification
    """
    print(f"Processing notifications for user: {user_code}")
    
    user_token = get_user_firebase_token(user_code)
    
    if not user_token:
        print(f"No FCM token found for user {user_code}")
        
        return f"No FCM token for user {user_code}"
    
    success, response = send_firebase_notification(
            registration_id=user_token,
            title=title,
            body=body,
        )
    
    return f"Sent notifications to user {user_code}"


@shared_task(name="app.tasks.send_reminder_notification")
def send_reminder_notification():
    """Send notifications for events happening tomorrow"""
    now = datetime.now(pytz.UTC)
    tomorrow_start = now + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(days=1)
    
    reminders = Notification.objects(
        type="reminder",
        due_time__gte=tomorrow_start,
        due_time__lt=tomorrow_end,
        notified=False
    )
    
    for reminder in reminders:
        user_token = get_user_firebase_token(reminder.user_code)
        
        if user_token:
            due_date = reminder.due_time.strftime("%B %d at %I:%M %p") if reminder.due_time else "tomorrow"
            reminder_message = f"{reminder.message} (Due: {due_date})"
            
            extra_data = {
                "due_time": str(reminder.due_time) if reminder.due_time else "0",
                "type": "reminder"
            }
            
            success, response = send_firebase_notification(
                registration_id=user_token,
                title=reminder.title,
                body=reminder_message,
                extra_data=extra_data
            )
            
            if success:
                reminder.update(set__notified=True)
                print(f"Reminder sent to {reminder.user_code}: {response}")
            else:
                print(f"Failed to send reminder: {response}")
    
    return f"Processed {reminders.count()} reminders"