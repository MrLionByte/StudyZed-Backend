from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField

# Create your models here.

class Email_temporary(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{6}$')], default=000000)
    no_of_try = models.IntegerField(default=0)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.email, self.otp}"

class UserAddon(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STUDENT', 'Student'),
        ('TUTOR', 'Tutor'),
    )
    role = models.CharField(choices=ROLE_CHOICES,blank=False, null=False, max_length=15)
    
    def __str__(self):
        return self.username
    
class Profile(models.Model):
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True, null=True)
    user = models.OneToOneField("UserAddon", on_delete=models.CASCADE ,blank=True, related_name="profile")
    phone = models.CharField(max_length=16, null=True, unique=True)
    profile_picture = CloudinaryField('image', blank=True)
    cover_picture = CloudinaryField('cover_image', blank=True)
    
    
    def __str__(self):
        return f"profile for {self.user.username}"