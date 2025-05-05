import logging
from mongoengine import connect
from django.conf import settings

logger = logging.getLogger(__name__)

def connect_to_mongo():
    try:
        connect(host=settings.MONGO_URI)
        logger.info("Successfully connected to MongoDB!")
    except Exception as e:
        logger.exception(f"Error connecting to MongoDB: {e}")
