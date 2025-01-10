from django.db import models
from dateutil.relativedelta import relativedelta 
from django.utils.timezone import now
import uuid 
from datetime import datetime

# Create your models here.


class Subscription(models.Model):
    class SubscriptionType(models.IntegerChoices):
        ONE_MONTH = 1, 'one-month'
        THREE_MONTHS = 3, 'three-months'
        SIX_MONTHS = 6, 'six-months'
        TWELVE_MONTHS = 12, 'twelve-months'
        
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tutor_code = models.CharField(max_length=150)
    session_code = models.CharField(max_length=150)
    subscription_type = models.IntegerField(choices=SubscriptionType.choices)
    created_at = models.DateField(null=True)
    updated_on = models.DateField(auto_now=True)
    expiry_time = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    
    
    def save(self, *args, **kwargs):
        print("CRAETED AT :", self.created_at)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(self.created_at, "%Y-%m-%d").date()
        if not self.expiry_time:
            self.expiry_time = self.created_at + relativedelta(months=int(self.subscription_type))
            
        super().save(*args, **kwargs)
        
    def is_expired(self):
        return now().date() > self.expiry_time
    
    def renew_subscription(self, subscription_type):
        self.subscription_type = subscription_type
        self.created_at = now().date()
        self.expiry_time = self.created_at + relativedelta(months=int(subscription_type))
        self.save()
        
    def __str__(self):
        return f"{self.session_code} of {self.tutor_code}"
         
    
class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription_key = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=(
        ("success", "Success"), ("failed", "Failed"), ("pending", "Pending"), ('refunded', 'Refunded')
        ))
    
    def __str__(self):
        return f"{self.payment_id} of {self.subscription_key.tutor_code}"
    
