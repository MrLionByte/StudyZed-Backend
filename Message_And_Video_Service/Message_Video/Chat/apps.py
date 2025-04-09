from django.apps import AppConfig
from .mongodb_connection import connect_to_mongo

class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Chat"

    def ready(self):
        connect_to_mongo()