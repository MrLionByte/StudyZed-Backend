from django.contrib import admin
from .models import StudentAssessment, StudentAssessmentResponse

# Register your models here.
class AssessmentResponseInline(admin.TabularInline):
    model = StudentAssessmentResponse
    extra = 1
    
class StudentAssessmentTable(admin.ModelAdmin):
    inlines = [AssessmentResponseInline]

admin.site.register(StudentAssessment, StudentAssessmentTable)