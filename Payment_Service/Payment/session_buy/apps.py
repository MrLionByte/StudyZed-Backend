from django.apps import AppConfig
import subprocess
import logging
import time

class SessionBuyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "session_buy"
    
    # def ready(self):
    #     try:
    #         print("Waiting for 5 seconds before starting the consumer...")
    #         time.sleep(5)
            
    #         print("Called Consumer Cmd : >>>")
    #         subprocess.Popen(['python', 'manage.py', 'consume_messages'])
    #     except Exception as e:
    #         print(f"Error running 'consume_messages' command: {e}")
    #         logging.error(f"Error running 'consume_messages' command: {e}")
