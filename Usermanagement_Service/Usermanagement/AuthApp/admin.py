from django.contrib import admin
from .models import UserAddon, Profile, Email_temporary
# Register your models here.

class ProfileInline(admin.TabularInline):
    model = Profile

class UserAddonTable(admin.ModelAdmin):
    inlines = [
        ProfileInline
    ]

admin.site.register(UserAddon, UserAddonTable)
admin.site.register(Email_temporary)