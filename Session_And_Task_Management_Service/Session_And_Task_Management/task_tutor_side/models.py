from django.db import models
from session_tutor.models import Session
# Create your models here.

class Tasks(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    notified = models.BooleanField(default=False) 
    
    def __str__(self):
       return f"Task: {self.title} (Session: {self.session})"
    