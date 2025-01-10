from django.db import models
from session_tutor.models import Session
# Create your models here.


class StudentsInSession(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_code = models.CharField(max_length=150)
    is_allowded = models.BooleanField(default=False)
    image_per_session = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None)
    name_per_session = models.CharField(max_length=250)
    joined_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    