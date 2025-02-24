from rest_framework import serializers, response, status
from .models import StudentsInSession, Session
from session_tutor.producer import kafka_producer


class EnterSessionSerializer(serializers.Serializer):
    session_code = serializers.CharField(write_only=True)
    student_code = serializers.CharField(required=True)
    
    class Meta:
        model = StudentsInSession
        fields = ["session", "student_code", "session"]
    
    def validate_session_code(self, value):
        print("222222")
        try:
            session = Session.objects.get(session_code=value)
        except Session.DoesNotExist:
            raise serializers.ValidationError("Session with the given code does not exist.")
        return session

    def create(self, validated_data):
        print("33333333")
        session = validated_data.pop("session_code")
        print("VALIDATED DAT :", validated_data.get('student_code'), session)
        # session_data = 
        if StudentsInSession.objects.filter(
            session=session, student_code=validated_data.get('student_code')).exists():
            raise serializers.ValidationError({
            "message": "You are already part of the session",
            "error": "exsist"
            })
        elif not session.is_active:
            raise serializers.ValidationError({
            "message": "This session is yet to be approved",
            "error": "not_approved"
            })
        student_code = validated_data.get('student_code')
        data = {
                "message": f"student :{student_code} has joined this session",
                "title": f"joined:{student_code}",
                "user_code": session.tutor_code,
                "type": "reminder",
            }
        kafka_producer.producer_message('student_joined', student_code, data)
        return StudentsInSession.objects.create(session=session, **validated_data)
        

class StudentSessionSerializer(serializers.ModelSerializer):
    session = session_name = serializers.CharField(source="session.session_code", read_only=True)
    session_name = serializers.CharField(source="session.session_name", read_only=True)
    tutor_code = serializers.CharField(source="session.tutor_code", read_only=True)

    class Meta:
        model = StudentsInSession
        fields = [
            'session',
            'session_name',
            'tutor_code',
            'student_code',
            'is_allowded', 
            'joined_on',
            'updated_on',
        ]