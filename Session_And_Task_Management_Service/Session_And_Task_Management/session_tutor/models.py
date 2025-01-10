from django.db import models
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
import uuid

# Create your models here.

class Session(models.Model):
    class SubscriptionType(models.IntegerChoices):
        ONE_MONTH = 1, 'one-month'
        THREE_MONTHS = 3, 'three-months'
        SIX_MONTHS = 6, 'six-months'
        TWELVE_MONTHS = 12, 'twelve-months'
    
    tutor_code = models.CharField(max_length=150)
    session_name = models.CharField(max_length=200)
    session_duration = models.IntegerField(choices=SubscriptionType.choices)
    session_discription = models.TextField(blank=True)
    session_code = models.CharField(max_length=150, unique=True, editable=False)
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    image = CloudinaryField("image", blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.session_code:
            unique_id = str(uuid.uuid4())[:6].upper()
            name_portion = ''.join(filter(str.isalnum, self.session_name))[:5].upper()
            self.session_code = f"{name_portion}-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.session_name} => {self.tutor_code}"
    
    