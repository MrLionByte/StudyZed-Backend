from django.contrib import admin
from .models import (
    Assessments, Assessment_Questions, Answer_Options
    )

# Register your models here.

class AnswerOptionsInline(admin.TabularInline):
    model = Answer_Options
    extra = 1

class QuestionsInline(admin.TabularInline):
    model = Assessment_Questions
    inlines = [AnswerOptionsInline]
    
class QuestionsTable(admin.ModelAdmin):
    inlines = [QuestionsInline]


admin.site.register(Assessments, QuestionsTable)