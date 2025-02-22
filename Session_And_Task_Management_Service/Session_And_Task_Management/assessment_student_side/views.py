from django.shortcuts import render
from rest_framework import views, generics ,status
from .models import (Session, StudentsInSession, StudentAssessmentResponse, 
                     StudentAssessment, Assessments, Assessment_Questions,
                     Answer_Options)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound, AuthenticationFailed, ParseError
from datetime import datetime
from .jwt_utils import decode_jwt_token
import jwt
from django.shortcuts import get_object_or_404
from .serializers import *
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


class AttendAssessmentViews(views.APIView):
    def post(self, request):
        data = request.data.get("data")
        assessment_id = request.data.get("assessment_id")
        print(">>> !! <<<",data, assessment_id)
        
        try:
            student = decode_jwt_token(request)
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            assessment_instance = Assessments.objects.get(id=assessment_id)
            student_code = student.get("user_code")
            student = StudentsInSession.objects.get(student_code=student_code)
            student_assessment = StudentAssessment.objects.create(
                student_session = student,
                assessment = assessment_instance,
                completed_on = datetime.now(),
                is_completed = True                
            )
            for question in data:
                print("99999 :: >",question)
                question_instance = Assessment_Questions.objects.get(id=question.get("questionId"))
                assessment_response = StudentAssessmentResponse.objects.create(
                    student_assessment = student_assessment,
                    question = question_instance,
                )
                print("?????? ",assessment_response)
                if question["questionType"] == "OPEN":
                    print("000999000")
                    assessment_response.open_response = question["answer"]
                    print("0003",assessment_response)
                    assessment_response.save()
                    print(assessment_response)
                else:
                    opted = Answer_Options.objects.get(id=question["answer"])
                    assessment_response.selected_option = opted
                    print("0003",assessment_response)
                    assessment_response.save()
                    print(assessment_response)
                    
            return Response({'2122'},status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            print(e)
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

class GetAttendedAssessmentsView(generics.ListAPIView):
    serializer_class = GetAttendedAssessmentsSerializers
    permission_classes = [AllowAny]
    queryset = StudentAssessment.objects.all()
    
    def get_queryset(self):
        try:
            user_data = decode_jwt_token(self.request)
            user = StudentsInSession.objects.get(
                student_code = user_data['user_code'])
            return StudentAssessment.objects.filter(student_session=user)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        
        except StudentsInSession.DoesNotExist:
            raise NotFound("User not found")
        
        except Exception as e:
            print("Error :",e)
            raise ParseError(str(e))