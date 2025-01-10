from django.contrib import admin
from .models import Wallet, WalletTransactions
# Register your models here.

class WalletHistoryInline(admin.TabularInline):
    model = WalletTransactions
    
class WalletTable(admin.ModelAdmin):
    inlines = [
        WalletHistoryInline
    ]
admin.site.register(Wallet, WalletTable)