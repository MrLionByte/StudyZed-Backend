from confluent_kafka import Producer
from confluent_kafka.error import ProduceError
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self, bootstrap_servers=str(settings.BOOTSTRAP_SERVERS)):
        self.producer = Producer({
            'bootstrap.servers' : bootstrap_servers
            })
    
    def producer_message(self, topic, key, value):
        try:
            self.producer.produce(topic, key=str(key), value=json.dumps(value))
            self.producer.flush()
        except Exception as e:
            logger.error(f"Error producing message: {e}")

kafka_producer = KafkaProducer()
    