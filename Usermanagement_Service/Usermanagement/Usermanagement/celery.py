from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Usermanagement.settings')
app = Celery('Usermanagement')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.task_default_queue = 'celery'
app.conf.worker_prefetch_multiplier = getattr(settings, 'CELERY_WORKER_PREFETCH_MULTIPLIER', 4)

# pip install django-celery-results