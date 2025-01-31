from rest_framework import generics, views, status
from .serializers import AllStudentsInAClassSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from AuthApp.models import UserAddon

# Create your views here.


class StudentDetailsView(generics.RetrieveAPIView):
    pass

class AllStudentsInAClassView (views.APIView):
    def post(self, request):
        students_codes = request.data.get("student_codes", [])
        print(students_codes)
        
        if not students_codes:
            return Response({"error": "No student codes provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        students = UserAddon.objects.filter(user_code__in=students_codes)
        print(students)
        serializer = AllStudentsInAClassSerializer(students ,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        