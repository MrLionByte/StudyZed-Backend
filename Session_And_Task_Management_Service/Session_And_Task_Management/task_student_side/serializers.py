from rest_framework import serializers
from .models import *


class TasksStudentAttendedSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedTask
        fields = "__all__"
        

class TasksThisMonthSerializer(serializers.ModelSerializer):
    attended = TasksStudentAttendedSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tasks
        fields = '__all__'