from django.db import models
from students_in_session.models import StudentsInSession, Session
from assessment_tutor_side.models import (
    Assessments, Assessment_Questions, Answer_Options)
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
    open_response = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True) 

    def __str__(self):
        return f"Response by {self.student_assessment.student_session.student_code} for {self.question}"
    