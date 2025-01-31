from django.contrib import admin
from .models import PriceOfSession, CouponForSession
# Register your models here.

admin.site.register(PriceOfSession)
admin.site.register(CouponForSession)