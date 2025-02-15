from rest_framework import serializers
from .models import Session
from students_in_session.models import StudentsInSession


class CreateSessionSerializers(serializers.ModelSerializer):
    session_duration = serializers.ChoiceField(choices=Session.SubscriptionType.choices)
    class Meta:
        model = Session
        fields = [
            "tutor_code", "session_name", "session_duration", 
            "session_discription", "session_code"
            ]
        read_only_fields = ["session_code"]
    
    def validate_session_duration(self, value):
        if value not in dict(Session.SubscriptionType.choices):
            raise serializers.ValidationError(f"{value} is not a valid choice for session_duration.")
        return value

    def validate(self, data):
        tutor_code = data.get("tutor_code")
        session_name = data.get("session_name")
        if Session.objects.filter(tutor_code=tutor_code, session_name=session_name).exists():
            print("ERROR OCCUR :", session_name, tutor_code)
            raise serializers.ValidationError(
                f"Session '{session_name}' already exists for tutor ID '{tutor_code}'."
            )
        return data

class GetSessionSerializers(serializers.Serializer):
    class Meta:
        model = Session
        fields = ['__all__']


class TutorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"

class AllStudentInSessions(serializers.ModelSerializer):
    class Meta:
        model = StudentsInSession
        fields = "__all__"

class ApprovedStudentsInSessions(serializers.ModelSerializer):
    class Meta:
        model = StudentsInSession
        fields = ["student_code"]