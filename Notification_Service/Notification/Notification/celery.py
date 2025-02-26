from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notification.settings')

app = Celery('Notification')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
# pip install django-celery-results