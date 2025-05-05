# your_app/management/commands/consume_messages.py
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import logging
from django.conf import settings
from session_buy.models import Subscription 
import time
import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consume messages from Kafka and process them'

    def handle(self, *args, **kwargs):
        self.consume_messages()

    def consume_messages(self):
        conf = {
            'bootstrap.servers': str(settings.BOOTSTRAP_SERVERS),
            'group.id': 'my-consumer-group',
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(conf)
        consumer.subscribe(['create-session'])

        try:
            while True:
                msg = consumer.poll(timeout=5.0)
                if msg is None:
                    logger.info("No new messages")
                    # continue
                else:
                    if msg.error():
                        logger.error(f"Error: {msg.error()}")
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            logger.error(f"End of partition reached: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                        else:
                            raise KafkaException(msg.error())
                    else:
                        message_value = json.loads(msg.value().decode('utf-8'))
                        logger.info(f"Received message: {message_value}")
                        session_code = message_value.get('session_code')

                        if session_code:
                            Subscription.objects.create(
                            session_code=session_code,
                            created_at = message_value.get('created_on'),
                            tutor_code=message_value.get('tutor_code'),
                            subscription_type=message_value.get('session_duration')
                            )
                
                time.sleep(5)
                logger.info(f"Woke up at: {datetime.datetime.now()}")
                
        except KeyboardInterrupt:
            logger.warning("Consumer stopped.")
        finally:
            consumer.close()
            logger.warning("Consumer closed.")
