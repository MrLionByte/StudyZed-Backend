from rest_framework import serializers
from .models import Tasks
from task_student_side.models import AssignedTask


class AttendedStudentsSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source="student.student_code")

    class Meta:
        model = AssignedTask
        fields = [
            "id",
            "student_code",
            "answer",
            "score",
            "completed_on",
            "is_late_submission",
        ]


class TasksSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="due_date")
    attended = AttendedStudentsSerializer(many=True, read_only=True)

    class Meta:
        model = Tasks
        fields = ["id", "title", "description", "created_at", "date", "attended"]

class AssignedTaskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedTask
        fields = ['score']  

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Score must be between 1 and 10.")
        return value

class TaskEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = '__all__' 
