from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import Assessments, Assessment_Questions, Answer_Options, Session
# Create your views here.


class CreateAssessmentView(generics.CreateAPIView):
    queryset = Assessments.objects.all()
    serializer_class = AssessmentsSerializer
    
    def perform_create(self, serializer):
        print("ASSESSMENT :", serializer)
        assessment = serializer.save()
        return assessment


class GetAssessmentView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GetAssessmentsSerializer

    def get_queryset(self):
        session_code = self.request.GET.get('session_code', '')
        print("SESSION :: >> ", session_code)
        session_key = Session.objects.get(session_code=session_code)
        print("SESSIOn KEy :",session_key)
        return Assessments.objects.filter(session_key=session_key)
    

class AddQuestionsToAssessmentView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AddQuestionsToAssessmentSerializers
    queryset = Assessment_Questions.objects.all()

