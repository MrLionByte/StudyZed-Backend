from rest_framework import serializers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Session
from students_in_session.models import StudentsInSession


class CreateSessionSerializers(serializers.ModelSerializer):
    session_duration = serializers.ChoiceField(choices=Session.SubscriptionType.choices)

    class Meta:
        model = Session
        fields = [
            "tutor_code",
            "session_name",
            "session_duration",
            "session_discription",
            "session_code",
        ]
        read_only_fields = ["session_code"]

    def validate_session_duration(self, value):
        if value not in dict(Session.SubscriptionType.choices):
            raise serializers.ValidationError(
                f"{value} is not a valid choice for session_duration."
            )
        return value

    def validate(
        self,
        data,
    ):
        tutor_code = data.get("tutor_code")
        session_name = data.get("session_name")
        if Session.objects.filter(
            tutor_code=tutor_code, session_name=session_name
        ).exists():
            raise serializers.ValidationError(
                f"Session '{session_name}' already exists for tutor ID '{tutor_code}'."
            )
        return data


class GetSessionSerializers(serializers.Serializer):
    class Meta:
        model = Session
        fields = ["__all__"]


class TutorSessionSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = "__all__"

    def get_student_count(self, obj):
        """Returns the count of students in a session."""
        return StudentsInSession.objects.filter(session=obj).count()

    def get_days_left(self, obj):
        """Calculates the number of days left in the session."""
        if obj.updated_at and obj.session_duration:
            created_at_datetime = datetime.combine(obj.created_at, datetime.min.time())
            expiry_date = created_at_datetime + relativedelta(months=obj.session_duration)            
            days_remaining = (expiry_date.date() - datetime.now().date()).days

            return max(days_remaining, 0) 
        return None


class AllStudentInSessions(serializers.ModelSerializer):
    class Meta:
        model = StudentsInSession
        fields = "__all__"


class ApprovedStudentsInSessions(serializers.ModelSerializer):
    class Meta:
        model = StudentsInSession
        fields = ["student_code"]

    
class UpdateSessionSerializer(serializers.ModelSerializer):
    days_left = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = '__all__'

    def update(self, instance, validated_data):
        if "image" in self.context["request"].FILES:
            instance.image = self.context["request"].FILES["image"]
            instance.save()
        return super().update(instance, validated_data)

    def get_days_left(self, obj):
        """Calculates the number of days left in the session."""
        if obj.updated_at and obj.session_duration:
            created_at_datetime = datetime.combine(obj.created_at, datetime.min.time())
            expiry_date = created_at_datetime + relativedelta(months=obj.session_duration)            
            days_remaining = (expiry_date.date() - datetime.now().date()).days

            return max(days_remaining, 0) 
        return None