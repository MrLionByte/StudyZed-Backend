from django.db import models, transaction
import uuid
from decimal import Decimal
# Create your models here.


class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'U.S. Dollar'),
        ('EUR', 'Euro'),
        ('CAD', 'Canadian Dollar'),
        ('CNY', 'Chinese Yuan'),
        ('INR', 'Indian Rupee'),
    ]
    account_number=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_code = models.CharField(max_length=150, unique=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    currency_mode = models.CharField(choices=CURRENCY_CHOICES, max_length=30, default="INR")
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    # added
    auto_credit = models.BooleanField(default=False) #Receive +
    auto_debit = models.BooleanField(default=False) #Withdraw -
    
    def __str__(self):
        return f"{self.user_code} ACC.NO : {self.account_number}"
    
class WalletTransactions(models.Model):
    wallet_transaction_id = models.CharField(max_length=100, default=uuid.uuid4, editable=False, unique=True)
    wallet_key = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=[('CREDIT', 'Received + '), ('DEBIT', 'Withdrawn - ')])
    tickets = models.CharField(max_length=12, choices=[('SOLVED', 'Solved'), ('RAISED', 'Raised')], blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ("BLOCKED", "Blocked")])
    currency = models.CharField(max_length=30, default="INR")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateField(auto_now_add=True)
    
    def _update_account_balance(self, *args, **kwargs):
        if self.transaction_type == "CREDIT":
            print("CREDIT")
            self.wallet_key.balance+=Decimal(self.amount)
        elif self.transaction_type == "DEBIT":
            print("DEBIT")
            if self.wallet_key.balance-self.amount < 0:
                raise Exception (f"you don't have balance for that, current balance is {self.wallet_key.balance}")
            self.wallet_key.balance -= Decimal(self.amount)
            print(self.wallet_key.balance)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        self._update_account_balance()
        super().save(*args, **kwargs)
        self.wallet_key.save()
        print("AFTER SAVE" ,self.wallet_key.balance)
    
    def __str__(self):
        return f"{self.amount} as {self.transaction_type} for {self.wallet_key.user_code}"
    