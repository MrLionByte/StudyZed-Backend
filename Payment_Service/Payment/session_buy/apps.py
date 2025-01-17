from django.apps import AppConfig
import subprocess
import logging
import time
import os

class SessionBuyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "session_buy"
    
    # lock_file = "/tmp/kafka_consumer.lock"
    
    # def ready(self):
    #     if os.environ.get("RUN_MAIN") == "true":
    #         print("SessionBuyConfig ready method called.")     
    #         if not os.path.exists(self.lock_file):
    #             try:
    #                 # time.sleep(10)
    #                 print("Called Consumer Cmd : >>>")
    #                 self._consumer_started = True
    #                 subprocess.Popen(['python', 'manage.py', 'consume_messages'])
    #             except Exception as e:
    #                 self._consumer_started = False
    #                 print(f"Error running 'consume_messages' command: {e}")
    #                 logging.error(f"Error running 'consume_messages' command: {e}")
    #         else:
    #             print("Consumer already started. Skipping...")