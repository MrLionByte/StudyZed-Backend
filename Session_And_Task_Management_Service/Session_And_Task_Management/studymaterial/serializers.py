from rest_framework import serializers
from .models import StudyMaterial

class StudyMaterialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudyMaterial
        fields = '__all__' 