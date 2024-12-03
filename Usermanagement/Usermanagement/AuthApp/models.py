from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserAddon(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
    )
    role = models.CharField(choices=ROLE_CHOICES,blank=False, null=False, max_length=15)
    phone = models.CharField(max_length=13, blank=True, null=True, unique=True)
    
    def __str__(self):
        return self.username
    
class Profile(models.Model):
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True, null=True)
    user = models.OneToOneField("UserAddon", on_delete=models.CASCADE ,blank=True, related_name="profile")
    
    def __str__(self):
        return f"profile for {self.user.username}"