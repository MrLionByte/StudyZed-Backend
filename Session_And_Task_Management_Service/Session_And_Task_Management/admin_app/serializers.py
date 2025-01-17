from rest_framework import serializers
from session_tutor.models import Session


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

