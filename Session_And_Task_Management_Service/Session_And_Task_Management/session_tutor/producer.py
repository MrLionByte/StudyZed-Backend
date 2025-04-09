from confluent_kafka import Producer
from confluent_kafka.error import ProduceError
from django.conf import settings
import json

class KafkaProducer:
    def __init__(self, bootstrap_servers=str(settings.BOOTSTRAP_SERVERS)):
        self.producer = Producer({
            'bootstrap.servers' : bootstrap_servers
            })
    
    def producer_message(self, topic, key, value):
        print("Producer working :", "topic :",topic, "key :", key, "value :",value)
        try:
            self.producer.produce(topic, key=str(key), value=json.dumps(value))
            self.producer.flush()
            print(f"MESSAGE TO TOPIC {topic} :=> {value}")
        except Exception as e:
            print(f'Producer error : {e}')

kafka_producer = KafkaProducer()
    