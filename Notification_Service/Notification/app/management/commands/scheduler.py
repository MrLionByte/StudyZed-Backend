# from datetime import datetime, timedelta
# import pytz
# from app.models import Notification, UserFCMToken
# from django.core.management.base import BaseCommand
# from django.db.models import Q
# from mongoengine.queryset.visitor import Q as MongoQ
# from app.firebase import send_firebase_notification

# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         tomorrow = datetime.now(pytz.UTC) + timedelta(days=1)
#         tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
#         tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
#         notifications = Notification.objects(
#             MongoQ(type="reminder") &
#             MongoQ(notified=False) &
#             MongoQ(is_read=False) &
#             MongoQ(due_time__gte=tomorrow_start) &
#             MongoQ(due_time__lte=tomorrow_end)
#         )
        
#         for notification in notifications:
#             token = UserFCMToken.objects(user_code=notification.user_code).first()
            
#             if token:
#                 success, response = send_firebase_notification(
#                     token.fcm_token,
#                     notification.title,
#                     notification.message
#                 )
                
#                 if success:
#                     notification.update(notified=True)
#                 else:
#                     print(f"Error sending notification {notification.id}: {response}")
#             else:
#                 print(f"No FCM token found for user_code: {notification.user_code}")

from django_celery_beat.models import PeriodicTask, CrontabSchedule

schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='22',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

PeriodicTask.objects.get_or_create(
    name='Send Daily Notifications',
    task='app.task.send_notification', 
    crontab=schedule,
    enabled=True,
)