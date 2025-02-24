# your_app/management/commands/consume_messages.py
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException, KafkaError
import json

from app.models import Notification 
import time
import datetime

class Command(BaseCommand):
    help = 'Consume messages from Kafka and process them'

    def handle(self, *args, **kwargs):
        self.start_notification_consumer()

    def start_notification_consumer(self):
        print("Starting Notification Kafka Consumer")
        conf = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'my-consumer-group',
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(conf)
        
        consumer.subscribe(['daily_task'])  # Subscribe to the Kafka topic

        try:
            while True:
                print("Polling Notification Kafka...")
                msg = consumer.poll(timeout=5.0)
                if msg is None:
                    print("No new messages")
                    # continue
                else:
                    if msg.error():
                        print(f"Error: {msg.error()}")
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                        else:
                            raise KafkaException(msg.error())
                    else:
                        message_value = json.loads(msg.value().decode('utf-8'))
                        print(f"Received message: {message_value}")
                        message = message_value.get('message')
                        task = message_value.get('task')
                        type = message_value.get('type')
                        student_codes = message_value.get('student_codes')
                        
                        if student_codes:
                            print(f"Processing session with code: {student_codes}")
                            for student in student_codes: 
                                notification = Notification(
                                        title = task.get("title"),
                                        message = message,
                                        user_code = student,
                                        type = type,
                                        due_time = task.get("due_date"),
                                )
                                notification.save()
                                print(f"Session created with code: {notification}")
                print(f"Sleeping at: {datetime.datetime.now()}")
                time.sleep(5)
                print(f"Woke up at: {datetime.datetime.now()}")
                
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()
            print("Consumer closed.")

