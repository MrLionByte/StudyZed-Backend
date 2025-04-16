from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
import uuid

# Create your models here.


class Email_temporary(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(
        max_length=6, validators=[RegexValidator(r"^\d{6}$")]
        )
    no_of_try = models.IntegerField(default=0)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email, self.otp}"


class UserAddon(AbstractUser):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("STUDENT", "Student"),
        ("TUTOR", "Tutor"),
    )
    role = models.CharField(
        choices=ROLE_CHOICES, blank=False, null=False, max_length=15
    )
    google_id = models.CharField(max_length=255, blank=True)
    user_code = models.CharField(max_length=15, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.user_code:
            unique_id = str(uuid.uuid4())[:7].upper()
            name_portion = ''.join(filter(str.isalnum, self.username))[:5].upper()
            self.user_code = f"{name_portion}-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username


class Profile(models.Model):
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True, null=True)
    user = models.OneToOneField(
        "UserAddon", on_delete=models.CASCADE, blank=True, related_name="profile"
    )
    phone = models.CharField(max_length=16, null=True, unique=True)
    profile_picture = CloudinaryField("image", blank=True)
    cover_picture = CloudinaryField("cover_image", blank=True)

    def __str__(self):
        return f"profile for {self.user.username}"
