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

class AssessmentResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False)
    question_type = serializers.ChoiceField(choices=["OPEN", "MULTIPLE_CHOICE","SINGLE_CHOICE"])
    answer = serializers.CharField(required=False)

class AttendAssessmentSerializers(serializers.Serializer):
    assessment_id = serializers.IntegerField(required=False)
    responses = AssessmentResponseSerializer(many=True)
    
    def validate(self, value):
        if not Assessments.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Assessment ID")
        return value


class GetAttendedAssessmentResponsesSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentAssessmentResponse
        fields = "__all__"

class GetAttendedAssessmentsSerializers(serializers.ModelSerializer):
    responses = GetAttendedAssessmentResponsesSerializers(many=True)
    class Meta:
        model = StudentAssessment
        fields = "__all__"
    