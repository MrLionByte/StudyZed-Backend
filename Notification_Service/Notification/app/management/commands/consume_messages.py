# Unified Commands For all Consumers 

from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import time
import datetime
import logging
from django.conf import settings
from app.models import Notification, UserFCMToken  
from app.tasks import send_notification_for_user

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Unified Kafka Consumer for multiple topics"


    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            nargs='+',
            default=["student_joined", "daily_task", "attended_task", "assessment", "assessment_attend"],
            help='List of topics to subscribe to'
        )

    def handle(self, *args, **kwargs):
        self.start_notification_consumer()


    def start_notification_consumer(self):
        logger.info("Starting Unified Kafka Consumer")

        conf = {
            "bootstrap.servers": str(settings.BOOTSTRAP_SERVERS),
            "group.id": "notification-consumer-group",
            "auto.offset.reset": "earliest",
        }
        consumer = Consumer(conf)

        topics = ["student_joined", "daily_task", "attended_task", "assessment", "assessment_attend"]
        consumer.subscribe(topics)

        try:
            while True:
                msg = consumer.poll(timeout=5.0)
                if msg is None:
                    print("No new messages")
                    logger.info("No new messages")
                    time.sleep(10)
                    continue
                elif msg.error():
                    logger.error(f"Error: {msg.error()}")
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.error(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        raise KafkaException(msg.error())
                else:
                    message_value = json.loads(msg.value().decode("utf-8"))
                    print(f"Received message from {msg.topic()}: {message_value}")
                    logger.info(f"Received message from {msg.topic()}: {message_value}")

                    if msg.topic() == "student_joined":
                        self.handle_student_joined(message_value)
                    elif msg.topic() == "daily_task":
                        self.handle_daily_task(message_value)
                    elif msg.topic() == "attended_task":
                        self.handle_attended_task(message_value)
                    elif msg.topic() == "assessment":
                        self.handle_assessment(message_value)
                    elif msg.topic() == "assessment_attend":
                        self.handle_assessment_attended(message_value)

                time.sleep(5)

        except KeyboardInterrupt:
            logger.error("Consumer stopped.")
        finally:
            consumer.close()
            logger.error("Consumer closed.")


    def handle_student_joined(self, message):
        try:
            notification = Notification.objects.create(
                title=message.get("title"),
                message=message.get("message"),
                user_code=message.get("user_code"),
                type=message.get("type"),
            )
            success = send_notification_for_user.apply(args=[message.get("user_code"), message.get("title"), message.get("message")])
           
            if success:
                notification.update(set__notified=True)
                print(f"Notification sent handle_student_joined")
        except Exception as e:
            print(f"Error at handle_student_joined : {str(e)}")
            logger.error(f"Error at handle_student_joined : {str(e)}")


    def handle_daily_task(self, message):
        processed_users = set()
        try:
            for student in message.get("student_codes", []):
                notification = Notification.objects.create(
                    title=message.get("task", {}).get("title"),
                    message=message.get("message"),
                    user_code=student,
                    type=message.get("type"),
                    due_time=message.get("task", {}).get("due_date"),
                )
                if student not in processed_users:
                    success = send_notification_for_user.apply(args=[student, message.get("task", {}).get("title"), message.get("message")])
     
                    processed_users.add(student)
                    if success:
                        notification.update(set__notified=True)
                        print(f"Notification sent handle_daily_task : {student}")
                    print("User added ", processed_users)
        except Exception as e:
            print(f"Error at handle_daily_task : {str(e)}")
            logger.error(f"Error at handle_daily_task : {str(e)}")


    def handle_attended_task(self, message):
        try:
            notification = Notification.objects.create(
                title=message.get("title"),
                message=message.get("message"),
                user_code=message.get("tutor_code"),
                type=message.get("type"),
            )
            success = send_notification_for_user.apply(args=[message.get("tutor_code"), message.get("title"), message.get("message")])
            if success:
                notification.update(set__notified=True)
                print(f"Notification sent handle_attended_task")
        except Exception as e:
            print(f"Error at handle_attended_task : {str(e)}")
            logger.error(f"Error at handle_attended_task : {str(e)}")
            

    def handle_assessment(self, message):
        processed_users = set()
        try:
            for student in message.get("student_codes", []):
                notification = Notification.objects.create(
                    title=message.get("title"),
                    message=message.get("message"),
                    user_code=student,
                    type=message.get("type"),
                )
                if student not in processed_users:
                    success = send_notification_for_user.apply(args=[student, message.get("title"), message.get("message")])
                    processed_users.add(student)
                    if success:
                        notification.update(set__notified=True)
                        print(f"Notification sent handle_assessment : {student}")
        except Exception as e:
            print(f"Error at handle_assessment : {str(e)}")
            logger.error(f"Error at handle_assessment : {str(e)}")


    def handle_assessment_attended(self, message):
        try:
            notification = Notification.objects.create(
                title=message.get("title"),
                message=message.get("message"),
                user_code=message.get("tutor_code"),
                type=message.get("type"),
            )
            success = send_notification_for_user.apply(args=[message.get("tutor_code"), message.get("title"), message.get("message")])
            if success:
                notification.update(set__notified=True)
                print(f"Notification sent handle_assessment_attended")
        except Exception as e:
            print(f"Error at handle_assessment_attended : {str(e)}")
            logger.error(f"Error at handle_assessment_attended : {str(e)}")
    