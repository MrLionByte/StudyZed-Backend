# Unified Commands For all Consumers 

from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import time
import datetime
from app.models import Notification  

class Command(BaseCommand):
    help = "Unified Kafka Consumer for multiple topics"

    def handle(self, *args, **kwargs):
        self.start_notification_consumer()

    def start_notification_consumer(self):
        print("Starting Unified Kafka Consumer")

        conf = {
            "bootstrap.servers": "kafka:9092",
            "group.id": "my-consumer-group",
            "auto.offset.reset": "earliest",
        }
        consumer = Consumer(conf)

        topics = ["student_joined", "daily_task", "attended_task", "assessment", "assessment_attend"]
        consumer.subscribe(topics)

        try:
            while True:
                print("Polling Kafka...")
                msg = consumer.poll(timeout=5.0)
                if msg is None:
                    print("No new messages")
                    time.sleep(5)
                    continue
                elif msg.error():
                    print(f"Error: {msg.error()}")
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        raise KafkaException(msg.error())
                else:
                    message_value = json.loads(msg.value().decode("utf-8"))
                    print(f"Received message from {msg.topic()}: {message_value}")

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
            print("Consumer stopped.")
        finally:
            consumer.close()
            print("Consumer closed.")

    def handle_student_joined(self, message):
        Notification.objects.create(
            title=message.get("title"),
            message=message.get("message"),
            user_code=message.get("user_code"),
            type=message.get("type"),
        )

    def handle_daily_task(self, message):
        for student in message.get("student_codes", []):
            Notification.objects.create(
                title=message.get("task", {}).get("title"),
                message=message.get("message"),
                user_code=student,
                type=message.get("type"),
                due_time=message.get("task", {}).get("due_date"),
            )

    def handle_attended_task(self, message):
        Notification.objects.create(
            title=message.get("title"),
            message=message.get("message"),
            user_code=message.get("tutor_code"),
            type=message.get("type"),
        )

    def handle_assessment(self, message):
        for student in message.get("student_codes", []):
            Notification.objects.create(
                title=message.get("title"),
                message=message.get("message"),
                user_code=student,
                type=message.get("type"),
            )

    def handle_assessment_attended(self, message):
        Notification.objects.create(
            title=message.get("title"),
            message=message.get("message"),
            user_code=message.get("tutor_code"),
            type=message.get("type"),
        )
