from django.db import models

# Create your models here.


class Class_management(models.Model):
    tutor_id = models.IntegerField()
    session_name = models.CharField(max_length=250, blank=False)
    unique_code = models.CharField(max_length=100, blank=False)
    is_payed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    