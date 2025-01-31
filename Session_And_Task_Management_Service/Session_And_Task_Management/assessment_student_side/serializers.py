from rest_framework import serializers
from assessment_tutor_side.models import (Assessments, Session, 
                                          Assessment_Questions, Answer_Options)
from .models import StudentAssessment, StudentAssessmentResponse


class AssessmentOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer_Options
        fields = "__all__"

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    options = AssessmentOptionSerializer(many=True, required=False)  

    class Meta:
        model = Assessment_Questions
        fields = "__all__"

class AssessmentsSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, required=False) 

    class Meta:
        model = Assessments
        fields = "__all__"
