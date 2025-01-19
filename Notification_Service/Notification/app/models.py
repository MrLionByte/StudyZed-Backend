from mongoengine import Document, StringField


class Notification(Document):
    title = StringField(required=True)
    message = StringField(required=True)
    created_at = StringField()