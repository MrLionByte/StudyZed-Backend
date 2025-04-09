import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Session_And_Task_Management.settings')

app = Celery('Session_And_Task_Management')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
