from django.apps import AppConfig
from .mongodb_connection import connect_to_mongo

class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        connect_to_mongo()
