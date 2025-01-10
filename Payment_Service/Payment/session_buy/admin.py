from django.contrib import admin
from .models import Subscription, Payment
# Register your models here.

class PaymentInline(admin.TabularInline):
    model = Payment
    
class PaymentTable(admin.ModelAdmin):
    inlines = [
        PaymentInline
    ]
admin.site.register(Subscription, PaymentTable)