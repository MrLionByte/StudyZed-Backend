from rest_framework import serializers
from .models import Assessments, Session, Assessment_Questions, Answer_Options


class AnswerOptionsSerializer(serializers.Serializer):
    option_no = serializers.IntegerField()
    option = serializers.IntegerField()
    is_correct = serializers.BooleanField()
    
    class Meta:
        model = Answer_Options
        fields = ["option_no", "option", "is_correct"]
    
class AssessmentQuestionsSerializer(serializers.Serializer):
    options = AnswerOptionsSerializer(many=True ,required=False)
    max_score = serializers.IntegerField()
    question_type = serializers.CharField(max_length=50)
    question= serializers.CharField(max_length=1200)
    
    class Meta:
        model = Assessment_Questions
        fields = ['question', 'max_score',
                  'question_type', 'options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Assessment_Questions.objects.create(
            **validated_data
        )
        for option in options_data:
            Answer_Options.objects.create(
                questions_key=question, **option
            )
        return question

class AssessmentsSerializer(serializers.Serializer):
    session_code = serializers.CharField(write_only=True)
    questions = AssessmentQuestionsSerializer(many=True, required=False)
    assessment_title = serializers.CharField(max_length=250)
    assessment_description = serializers.CharField(required=False)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    
    class Meta:
        model = Assessments
        fields = [
            "session_code",
            "assessment_title",
            "assessment_description",
            "start_time",
            "end_time",
            "questions",
        ]
        
    def validate(self, data):
        print("validate :: => ", data)
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError(
                'End time must be after start time'
            )
        return data
    
    def create(self, validated_data):
        session_code = validated_data.pop("session_code")
        try:
            session = Session.objects.get(session_code=session_code)
        except Session.DoesNotExist:
            raise serializers.ValidationError(
                {'session_code': 'Invalid session code.'}
                )
        
        questions_data = validated_data.pop('questions', [])
        
        assessment = Assessments.objects.create(
            session_key=session,
            **validated_data
        )
        
        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            
            # Create question
            question = Assessment_Questions.objects.create(
                assessment_key=assessment,
                **question_data
            )
            
            # Create options if question type is multiple choice
            if question.question_type == 'MLC':
                # Validate at least one correct option
                if not any(option['is_correct'] for option in options_data):
                    raise serializers.ValidationError(
                        f"Question '{question.question}' must have at least one correct option"
                    )
                
                # Validate option numbers are unique
                option_numbers = [option['option_no'] for option in options_data]
                if len(option_numbers) != len(set(option_numbers)):
                    raise serializers.ValidationError(
                        f"Question '{question.question}' has duplicate option numbers"
                    )
                
                # Create options
                for option_data in options_data:
                    Answer_Options.objects.create(
                        questions_key=question,
                        **option_data
                    )
        
        return assessment
    
            
class CreateAssessmentSerializers(serializers.ModelSerializer):
    session_code = serializers.CharField(write_only=True)
    session_key = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Assessments
        fields = ['session_code', 'session_key','assessment_title', 'start_time', 'end_time']

    def validate(self, data):
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError(
                "End time must be after start time.")

        return data

    def create(self, validated_data):
        session_code = validated_data.pop('session_code', None)
        try:
            session = Session.objects.get(session_code=session_code)
        except Session.DoesNotExist:
            raise serializers.ValidationError({'session_code': 'Invalid session code.'})
        validated_data['session_key'] = session
        return Assessments.objects.create(**validated_data)

class AddQuestionsToAssessmentSerializers(serializers.ModelSerializer):
    assessment_key = serializers.PrimaryKeyRelatedField(
        queryset=Assessments.objects.all(), write_only=True)

    class Meta:
        model = Assessment_Questions
        fields = ['assessment_key', 'question', 'max_score',
                  'question_type']
    
    def create(self, validated_data):
        print(validated_data)
        assessment = validated_data.pop('assessment_key')
        validated_data['assessment_key'] = assessment
        return Assessment_Questions.objects.create(**validated_data)


class GetAnswerOptionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Answer_Options
        fields = "__all__"
    
class GetAssessmentQuestionsSerializer(serializers.ModelSerializer):
    options = AnswerOptionsSerializer(many=True ,required=False)
    
    class Meta:
        model = Assessment_Questions
        fields = "__all__"

class GetAssessmentsSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionsSerializer(many=True, required=False)
    
    class Meta:
        model = Assessments
        fields = "__all__"