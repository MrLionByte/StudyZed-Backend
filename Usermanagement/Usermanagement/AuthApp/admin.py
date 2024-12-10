from django.contrib import admin
from .models import UserAddon, Profile, Email_temporary
# Register your models here.

admin.site.register(UserAddon)
admin.site.register(Profile)
admin.site.register(Email_temporary)