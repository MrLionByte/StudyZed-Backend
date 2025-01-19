from django.contrib import admin
from mongoengine.django.admin import MongoEngineModelAdmin
from .models import Notification  # Assuming this is your MongoEngine model

class NotificationAdmin(MongoEngineModelAdmin):
    list_display = ['title', 'message', 'created_at']  # Fields to display in the list view

admin.site.register(Notification, NotificationAdmin)
