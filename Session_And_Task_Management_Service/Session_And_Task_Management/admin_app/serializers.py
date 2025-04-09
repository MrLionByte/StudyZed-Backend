from rest_framework import serializers
from session_tutor.models import Session
from assessment_tutor_side.models import Assessments
from task_tutor_side.models import Tasks


class SeeSessionToApproveSerializers(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class ApproveSessionSerializer(serializers.ModelSerializer):
    session_code = serializers.CharField(required=True)
    is_active = serializers.BooleanField()
    
    class Meta:
        model = Session
        fields = ['session_code', 'is_active']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'session_name', 'session_code', 'session_grade', 
                 'session_duration', 'is_active', 'created_at', 'start_date']

class AssessmentSerializer(serializers.ModelSerializer):
    session_code = serializers.CharField(source='session_key.session_code', read_only=True)
    
    class Meta:
        model = Assessments
        fields = ['id', 'assessment_title', 'assessment_description', 'created_on',
                 'total_mark', 'start_time', 'end_time', 'session_code']

class TaskSerializer(serializers.ModelSerializer):
    session_code = serializers.CharField(source='session.session_code', read_only=True)
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 
                 'notified', 'session_code', 'session_name', 'is_overdue']
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.due_date < timezone.now() and not obj.notified