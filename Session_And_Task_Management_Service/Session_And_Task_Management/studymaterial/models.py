from django.db import models
from session_tutor.models import Session

# Create your models here.

class StudyMaterial(models.Model):
    session_key = models.ForeignKey(
        Session, to_field="session_code", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    type = models.CharField(max_length=50, blank=True)
    link = models.CharField(max_length=200, blank=True)
    created_on = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
