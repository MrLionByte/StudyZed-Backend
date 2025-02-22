from django.db import models
from students_in_session.models import StudentsInSession, Session
from assessment_tutor_side.models import (
    Assessments, Assessment_Questions, Answer_Options)
from django.utils.timezone import make_aware, is_aware
# Create your models here.

class StudentAssessment(models.Model):
    student_session = models.ForeignKey(StudentsInSession,
                            on_delete=models.CASCADE,
                            related_name="student")
    assessment = models.ForeignKey(Assessments, on_delete=models.CASCADE,
                                   related_name="assessment")
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    started_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    is_late_submission = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student_session} => {self.assessment}"
    
    def save(self, *args, **kwargs):
        if not is_aware(self.completed_on):
            self.completed_on = make_aware(self.completed_on)
        if hasattr(self.assessment, 'end_time'): 
            if not is_aware(self.assessment.end_time):
                self.assessment.end_time = make_aware(self.assessment.end_time)

            if self.completed_on > self.assessment.end_time:
                self.is_late_submission = True
                
        super().save(*args, **kwargs)
    

class StudentAssessmentResponse(models.Model):
    student_assessment = models.ForeignKey(
        StudentAssessment, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Assessment_Questions,
                                 on_delete=models.CASCADE,
                                 related_name="responses")
    selected_option = models.ForeignKey(Answer_Options,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responses"
    )
    mark = models.PositiveIntegerField(blank=True, null=True)
    open_response = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True) 

    def __str__(self):
        return f"Response by {self.student_assessment.student_session.student_code} for {self.question}"
    
    def save(self, *args, **kwargs):
        if self.selected_option:
            if not self.is_correct:
                self.is_correct = self.selected_option.is_correct
                if self.is_correct:
                    self.mark = self.question.max_score or 0
                    
                    self.student_assessment.score = (
                        self.student_assessment.score or 0
                    ) + self.question.max_score
                    self.student_assessment.save()
        
        super().save(*args, **kwargs)
                

        
        