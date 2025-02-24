
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
        
        consumer.subscribe(['assessment_attend'])  # Subscribe to the Kafka topic

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
                        title = message_value.get('title')
                        type = message_value.get('type')
                        tutor_code = message_value.get('tutor_code')
                        
                        if tutor_code:
                            print(f"Processing session with code: {title}")
                        
                            notification = Notification(
                                    title = title,
                                    message = message,
                                    user_code = tutor_code,
                                    type = type,
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