from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAdminUser
from AuthApp.models import UserAddon
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework import status, generics

# Create your views here.

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_superuser:
            return Response({"detail": "Admin logged in successfully."})
        return Response({"detail": "Not authorized."}, status=403)
    
class AdminBlockUserView(generics.UpdateAPIView):
    queryset = UserAddon.objects.all()
    serializer_class = UserBlockSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        if not request.user.is_superuser:
            return Response({"detail": "You do not have permission to block/unblock users."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)