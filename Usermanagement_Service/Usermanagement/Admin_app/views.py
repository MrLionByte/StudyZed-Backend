from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAdminUser
from AuthApp.models import UserAddon
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework import status, generics
from .utils.response import api_response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

# Create your views here.

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AdminTokenObtainPairSerializer(data=request.data, context={'request': request})
        print("1111",serializer)
        try:
            serializer.is_valid(raise_exception=True)
            user = UserAddon.objects.get(username=request.data.get("username"))
            admin_data_serializer = AdminSerializer(user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            response = Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": admin_data_serializer.data,
                    "role": user.role,
                    "message": "Logged in successfully",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )
            return response
        
        except Exception as e:
            error_message = str(e.detail if hasattr(e, 'detail') else e)
            print(error_message, e)
            return Response(
                {"error": error_message, "auth-status": "failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        

class AdminAllTutorsListView(generics.ListAPIView):
    # permission_classes = [IsAdminUser]
    permission_classes = [AllowAny]
    serializer_class = UserAddonSerializer

    def get_queryset(self):
        return UserAddon.objects.filter(role='TUTOR')


class AdminAllStudentsListView(generics.ListAPIView):
    # permission_classes = [IsAdminUser]
    permission_classes = [AllowAny]
    serializer_class = UserAddonSerializer
    
    def get_queryset(self):
        print("QUERRy 11")
        return UserAddon.objects.filter(role="STUDENT")
    

class AdminBlockUserView(generics.UpdateAPIView):
    queryset = UserAddon.objects.all()
    serializer_class = UserBlockSerializer
    # permission_classes = [IsAdminUser]
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        print(user.is_active)
        # if not request.user.is_superuser:
        #     return Response({"detail": "You do not have permission to block/unblock users."},
        #                     status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)