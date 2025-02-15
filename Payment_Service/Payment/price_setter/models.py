from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Create your models here.

class PriceOfSession(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the session")
    duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], default=1
    )
    offer = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def final_price(self):
        """
        Calculate the final price after applying the offer percentage.
        """
        return self.amount * (Decimal(1) - Decimal(self.offer) / Decimal(100))

    def __str__(self):
        return f"X - {self.amount} => ${self.final_price():.2f}"
    
    
class CouponForSession(models.Model):
    session = models.ForeignKey(PriceOfSession, on_delete=models.CASCADE, related_name="coupons")
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, 
        )
    discount_percentage = models.PositiveIntegerField(
        null=True, blank=True,
        )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def apply_discount(self, base_price):
        """
        Calculate the discounted price based on the coupon.
        """
        if self.discount_amount:
            return max(base_price - self.discount_amount, 0)
        elif self.discount_percentage:
            return base_price * (1 - self.discount_percentage / 100)
        return base_price

    def __str__(self):
        return f"Coupon {self.code}"
