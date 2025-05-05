import logging
from rest_framework import generics, views, status
from .serializers import AllStudentsInAClassSerializer, BatchMatesInAClassSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from AuthApp.models import UserAddon

# Create your views here.
logger = logging.getLogger(__name__)

class StudentDetailsView(generics.RetrieveAPIView):
    pass

class AllStudentsInAClassView (views.APIView):
    def post(self, request):
        student_codes = request.data
        logger.info("Students user-codes", extra={'data': student_codes})
        if not student_codes:
            logger.error('No student codes provided', extra={'data': request.data})
            return Response({"error": "No student codes provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        students = UserAddon.objects.filter(user_code__in=student_codes)
        serializer = AllStudentsInAClassSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        

class TutorOfSessionDetailsView(views.APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        tutor_code = request.query_params.get("tutor_code")
        tutor = UserAddon.objects.get(user_code = tutor_code)
        data = {
            "tutor_code":tutor_code,
            "tutor_id": tutor.id,
            "tutor_name":tutor.first_name,
            "tutor_username": tutor.username
        }
        return Response({"data": data}, status=status.HTTP_200_OK)


class AllBatchMatesInAClassView (views.APIView):
    def post(self, request):
        student_codes = request.data
        logger.info("Students user-codes", extra={'data': student_codes})
        
        if not student_codes:
            logger.error('No student codes provided', extra={'data': request.data})
            return Response({"error": "No student codes provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        students = UserAddon.objects.filter(user_code__in=student_codes)
        serializer = BatchMatesInAClassSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)