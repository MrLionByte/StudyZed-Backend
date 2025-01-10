from rest_framework import serializers
from .models import Session


class CreateSessionSerializers(serializers.ModelSerializer):
    session_duration = serializers.ChoiceField(choices=Session.SubscriptionType.choices)
    class Meta:
        model = Session
        fields = [
            "tutor_code", "session_name", "session_duration", "session_discription"
            ]
    
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