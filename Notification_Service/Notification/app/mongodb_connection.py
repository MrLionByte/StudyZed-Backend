from mongoengine import connect
from django.conf import settings

def connect_to_mongo():
    try:
        connect(host=settings.MONGO_URI)
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
