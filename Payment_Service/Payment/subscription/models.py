from django.db import models
from dateutil.relativedelta import relativedelta 
import uuid 

# Create your models here.


class Subscription(models.Model):
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tutor_code = models.CharField(max_length=150)
    subscription_type = models.CharField(
         max_length=15,
        choices=[(12, 'twelve-months'),(6, "six-months"), (3, "three-months")]
        )
    purchased_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    expiry_time = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sessions_purchased = models.PositiveIntegerField()
    sessions_remaining = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        if not self.expiry_time:
            self.expiry_time = self.purchased_on + relativedelta(months=int(self.subscription_type))
        
        if self._state.adding:
            self.sessions_remaining += self.sessions_purchased
            
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return f"{self.subscription_id} of {self.tutor_code}"
         
    
class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription_key = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=(
        ("success", "Success"), ("failed", "Failed"), ("pending", "Pending"), ('refunded', 'Refunded')
        ))
    
    def __str__(self):
        return f"{self.payment_id} of {self.subscription.tutor_code}"
    
