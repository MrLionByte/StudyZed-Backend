# your_app/management/commands/consume_messages.py
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
from session_buy.models import Subscription 
import time

class Command(BaseCommand):
    help = 'Consume messages from Kafka and process them'

    def handle(self, *args, **kwargs):
        self.consume_messages()

    def consume_messages(self):
        print("Starting Kafka Consumer")
        conf = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'my-consumer-group',
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(conf)
        consumer.subscribe(['create-session'])

        try:
            print("Consuming messages...")
            while True:
                msg = consumer.poll(timeout=5.0)
                if msg is None:
                    print("No new messages")
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        raise KafkaException(msg.error())
                else:
                    message_value = json.loads(msg.value().decode('utf-8'))
                    print(f"Received message: {message_value}")
                    session_code = message_value.get('session_code')

                    if session_code:
                        print(f"Processing session with code: {session_code}")
                        Subscription.objects.create(
                            session_code=session_code,
                            created_at = message_value.get('created_on'),
                            tutor_code=message_value.get('tutor_code'),
                            subscription_type=message_value.get('session_duration')
                        )
                        print(f"Session created with code: {session_code}")
                time.sleep(20)
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()
            print("Consumer closed.")
