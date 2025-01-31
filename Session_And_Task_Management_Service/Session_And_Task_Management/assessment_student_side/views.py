from django.shortcuts import render
from rest_framework import views, generics ,status
from .models import Session, StudentsInSession, StudentAssessmentResponse, StudentAssessment, Assessments
from rest_framework.response import Response

from .serializers import AssessmentsSerializer
# Create your views here.

class GetAssessmentsForStudentViews(views.APIView):
    def get(self, request):
        session_code = request.GET.get("session_code")

        try:
            session = Session.objects.get(session_code=session_code)
            assessments = Assessments.objects.filter(session_key=session)
            serializer = AssessmentsSerializer(assessments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        