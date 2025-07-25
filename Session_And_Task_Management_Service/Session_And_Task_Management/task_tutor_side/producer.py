# tasks.py
import logging
from datetime import datetime, timedelta
from confluent_kafka import Producer
import json
from .models import Tasks
from kafka import KafkaProducer
from students_in_session.models import StudentsInSession
from confluent_kafka.error import ProduceError
from django.conf import settings

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
            logger.error(f'Producer error: {e}')

kafka_producer = KafkaProducer()