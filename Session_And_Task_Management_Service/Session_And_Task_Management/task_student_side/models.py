from django.db import models
from task_tutor_side.models import *
from students_in_session.models import StudentsInSession
from django.utils import timezone
# Create your models here.

class AssignedTask(models.Model):
    student = models.ForeignKey(StudentsInSession, on_delete=models.CASCADE, related_name='attended')
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, related_name="attended")
    answer = models.TextField()
    completed_on = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_late_submission = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student} >> {self.task.title}"

    def save(self, *args, **kwargs):
     
        if self.completed_on is None:
            self.completed_on = timezone.now()
        
        due_date = self.task.due_date
        if due_date and timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date)
        
        if timezone.is_naive(self.completed_on):
            self.completed_on = timezone.make_aware(self.completed_on)
        
        if due_date and self.completed_on > due_date:
            self.is_late_submission = True

        super().save(*args, **kwargs)
