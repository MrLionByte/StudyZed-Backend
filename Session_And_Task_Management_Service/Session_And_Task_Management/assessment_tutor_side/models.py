from django.db import models
from session_tutor.models import Session

# Create your models here.

class Assessments(models.Model):
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE)
    assessment_title = models.CharField(max_length=250)
    assessment_description = models.TextField(blank=True)
    created_on = models.DateField(auto_now_add=True)
    total_mark = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def __str__(self):
        return f"{self.assessment_title} on => {self.session_key.session_code}"

class Assessment_Questions(models.Model):
    assessment_key = models.ForeignKey(Assessments, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField(max_length=1250)
    max_score = models.PositiveIntegerField()
    created_on = models.DateField(auto_now_add=True)
    question_type = models.CharField(
        max_length=50,
        choices=[
            ("MLC", "Multiple Choice"),
            ("OPEN", "Open-Ended"),
        ],
        default="OPEN",
    )
    
    def save(self, *args, **kwargs):
        self.assessment_key.total_mark += self.max_score
        if self.pk:
            old_mark = Assessment_Questions.objects.get(
                pk=self.pk).max_score
            self.assessment_key.total_mark -= old_mark
        
        self.assessment_key.total_mark += self.max_score
        self.assessment_key.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.assessment_key} => {self.question_type}"
    
    
class Answer_Options(models.Model):
    questions_key = models.ForeignKey(Assessment_Questions,  on_delete=models.CASCADE, related_name="options")
    option_no = models.PositiveIntegerField()
    option = models.TextField(max_length=1250)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.questions_key} => {self.option}"
    