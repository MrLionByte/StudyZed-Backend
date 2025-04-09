# tasks.py
from datetime import datetime, timedelta
from confluent_kafka import Producer
import json
from .models import Tasks
from kafka import KafkaProducer
from students_in_session.models import StudentsInSession
from confluent_kafka.error import ProduceError
from django.conf import settings

print("PRODUCER :::", settings.BOOTSTRAP_SERVERS)
class KafkaProducer:
    def __init__(self, bootstrap_servers=str(settings.BOOTSTRAP_SERVERS)):
        self.producer = Producer({
            'bootstrap.servers' : bootstrap_servers
            })
    
    def producer_message(self, topic, key, value):
        print("Notification Producer working :", "topic :",topic, "key :", key, "value :",value)
        try:
            self.producer.produce(topic, key=str(key), value=json.dumps(value))
            self.producer.flush()
            print(f"MESSAGE TO TOPIC {topic} :=> {value}")
        except Exception as e:
            print(f'Producer error : {e}')

kafka_producer = KafkaProducer()





# producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

# def check_daily_tasks():
#     print("Kafka for daily task is running <<<==============>>>>")
#     today = datetime.now().date()
#     tomorrow = today + timedelta(days=1)
    
#     # Get tasks due tomorrow that haven't been notified yet
#     task = Tasks.objects.filter(
#         due_date__date=tomorrow,
#         notified=False
#     ).first()
    
#     if not task:
#         print("✅ No tasks due for tomorrow.")
#         return  # Exit if no tasks are found
    
#     session = task.session
#     student_codes = list(StudentsInSession.objects.filter(session=session).values_list('student_code', flat=True))

#     notification = {
#         'task_id': task.id,
#         'title': task.title,
#         'description': task.description,
#         'due_date': task.due_date.isoformat(),
#         'student_codes': student_codes
#     }
    
#     # Send to Kafka topic
#     try:
#         producer.send('daily_tasks', value=notification)
#         task.notified = True
#         task.save()
#         print(f"✅ Task {task.id} notification sent successfully!")
#     except Exception as e:
#         print(f"❌ Error sending notification for task {task.id}: {str(e)}")

# from confluent_kafka import Producer
# from confluent_kafka.error import ProduceError
# from django.conf import settings

# class KafkaProducer:
#     def __init__(self, bootstrap_servers='kafka:9092'):
#         self.producer = Producer({
#             'bootstrap.servers' : bootstrap_servers
#             })
    
#     def producer_message(self, topic, key, value):
#         print("Producer working :", "topic :",topic, "key :", key, "value :",value)
#         try:
#             self.producer.produce(topic, key=str(key), value=json.dumps(value))
#             self.producer.flush()
#             print(f"MESSAGE TO TOPIC {topic} :=> {value}")
#         except Exception as e:
#             print(f'Producer error : {e}')

# kafka_producer = KafkaProducer()
    