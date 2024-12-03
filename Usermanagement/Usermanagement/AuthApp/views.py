from django.shortcuts import render
from .models import UserAddon
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, OTPVerificationSerializer, EmailVerificationSerializer, PasswordResetSerializer
from rest_framework.views import APIView
from .mails import send_verification_email
from django.utils.timezone import now
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
# Create your views here.

class SignupEmailProcedureView(generics.CreateAPIView):
    
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try :
            
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            email = serializer.validated_data["email"]
            email_status = send_verification_email(email)
            print(f"EMAIL STATUS : {email_status}")
            if not email_status["success"]:
                     return Response(
                         {"error": email_status["message"]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            request.session['validationsteps'] = {
                        'email': email,
                        'otp' : email_status['otp'],
                        'no_of_try': 0,
                        'created_at': email_status['created_at'].isoformat(),
                        'expires_at': email_status['expires_at'].isoformat(),
                    }
            print(f"DATA IN SESSION : {request.session['validationsteps']}")
            return Response ({"message":"Email is valid and ready for OTP"}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response(
                        {"error": f"Faied to validate Email:, {e}"},
                    )
    

class SignupOTPVerificationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer
    def post(self, request):
        request.session["validationsteps"]['no_of_try'] = int(request.session["validationsteps"].get('no_of_try')) + 1
        request.session.modified = True
        print(f"DATA IN SESSION AFTER TRY : {request.session['validationsteps']}")
        serializer = self.get_serializer(data=request.data)
        try:
            if request.session["validationsteps"]['no_of_try'] > 5:
                return Response(
                        {"error": "Maximum tries exceeded."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            print(request.session['validationsteps'])
            return Response(
                {"message": "OTP verified successfully. Email is confirmed."},
                status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                        {"error": f"Faied to verify OTP:, {e}"},
                    )
        
class SignupUserDetailsView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        validated_data = serializer.validated_data
        user = serializer.create(validated_data)
        
        return Response(
            {"message": "User created successfully.", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer
    print("WORKING")
    
    def post(self, request, *args, **kwargs):
        try:
            if self.request.resolver_match.url_name == 'forgot_password':
                return self.forgot_password(request)
            print("ACTIOn : 000")
            return self.handle_login(request)
        except Exception as e:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
    def handle_login(self, request, *args, **kwargs):
        print("    MMMM     ::")
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        print("USER :", user)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
                
            response = Response ({
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)
                
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly = True,
                secure=True,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True
            )
            return response
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    def forgot_password(self,request):
        serializer = self.serializer_class(data = request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        email = serializer.validated_data['email']
        user = UserAddon.objects.get(email=email)
        
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        rest_url = f"http://127.0.0.1:8000/reset-password/{uidb64}/{token}/"
        return Response({"reset_url":f"{rest_url}"}, status=status.HTTP_200_OK)
        
class UploadProfile(APIView):
    permission_classes = [IsAuthenticated]
    pass
