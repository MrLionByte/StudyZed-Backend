import redis
import json
from .models import Email_temporary, UserAddon
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from rest_framework.views import APIView
from .mails import send_verification_email, send_forgot_password_email, resend_otp_verification_email
from django.utils.timezone import now
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from celery.result import AsyncResult
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.contrib.auth.hashers import make_password
import random
import string
from google.oauth2 import id_token


# Create your views here.

redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

## USER SIGN-UP EMAIL {


class SignupEmailProcedureView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        temp_mail = request.data["email"]
        if Email_temporary.objects.filter(email=temp_mail).exists():
            Email_temporary.objects.filter(email=temp_mail).delete()
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            print("SER EMAIl :", email)
            email_task = send_verification_email.delay(email)
            result = AsyncResult(email_task.id)
            print("RESULT :", result.get(), "  :::: ", result.result)
            if result.status == "PENDING":
                print("WORKING 133")
                return Response(
                    {"error": "ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            data = result.get()
            expires_at = timezone.make_aware(
                data["task"]["expires_at"], timezone=ZoneInfo("UTC")
            )
            print(type(expires_at))
            print("REDIS : ", redis_client.hgetall(email))
            new_temp_data = Email_temporary.objects.create(
                email=email, otp=data["task"]["otp"], expires_at=expires_at
            )

            return Response(
                {
                    "message": "Email verification success",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print("Error details: ", e)
            return Response(
                {"message": f"Email verification failed {e}", "auth-status": "failure"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {
                    "message": f"Email verification failed, email already in use",
                    "error": e,
                },
                status=status.HTTP_409_CONFLICT,
            )


## USER SIGN-UP EMAIL }


## USER SIGN-UP OTP VERIFICATION {


@method_decorator(csrf_exempt, name="dispatch")
class SignupOTPVerificationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        print("WORKING")
        serializer = self.get_serializer(data=request.data)
        try:
            print("SER ", serializer)
            user_under_verification = Email_temporary.objects.get(
                email=request.data["email"]
            )
            print("user_under_verification :", user_under_verification)
            user_under_verification.no_of_try += 1

            key = request.data["email"]
            print("REDIS TO INCRESE: ", redis_client.hgetall(key))
            redis_client.hincrby(key, "resend_count", 1)
            print(" :: ", redis_client.hgetall(key))

            user_under_verification.save()
            # if request.session["validationsteps"]['no_of_try'] > 5:
            if user_under_verification.no_of_try > 5:
                return Response(
                    {"error": "Maximum tries exceeded."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if not serializer.is_valid():
                print("Error ser", serializer.errors)
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # print(request.session['validationsteps'])
            user_under_verification.is_authenticated = True
            user_under_verification.save()
            return Response(
                {
                    "message": "OTP verified successfully. Email is confirmed.",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Faied to verify OTP:, {e}", "auth-status": "failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP OTP VERIFICATION }


## USER SIGN-UP OTP RESEND {


@method_decorator(csrf_exempt, name="dispatch")
class SignupOTPResendView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        temp_mail = request.data["email"]
        if Email_temporary.objects.filter(email=temp_mail).exists():
            Email_temporary.objects.filter(email=temp_mail).delete()
        serializer = self.get_serializer(data=request.data)
        try:
            email = temp_mail
            print("SER EMAIl :", email)
            email_task = resend_otp_verification_email.delay(email)
            result = AsyncResult(email_task.id)
            print("RESULT :", result.get(), "  :::: ", result.result)
            if result.status == "PENDING":
                print("WORKING ERROR")
                return Response(
                    {"error": "ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            data = result.get()
            expires_at = timezone.make_aware(
                data["task"]["expires_at"], timezone=ZoneInfo("UTC")
            )
            print(type(expires_at))
            print("REDIS : ", redis_client.hgetall(email))
            new_temp_data = Email_temporary.objects.create(
                email=email, otp=data["task"]["otp"], expires_at=expires_at
            )

            return Response(
                {
                    "message": "OTP resend successfully",
                    "auth-status": "resend",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print("Error details: ", e)
            return Response(
                {"message": f"OTP resend failed {e}", "auth-status": "failure"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

## USER SIGN-UP OTP RESEND }


## USER SIGN-UP ADD USER DETAILS {


class SignupUserDetailsView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request):
        try:
            print("PRINT REQUEST:", request.data)
            email_confirmation = Email_temporary.objects.get(
                email=request.data["email"]
            )

            if email_confirmation is None:
                return Response(
                    {
                        "error": "Email is not confirmed.Retry from email verification",
                        "auth-status": "unauthorized",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            serializer = self.get_serializer(data=request.data)
            print("SERILIZE REQUEST:", serializer)
            if not serializer.is_valid():
                print("Error in serializer: ", serializer.errors)
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data
            user = serializer.create(validated_data)
            print("WORKING USER", user)
            # email_confirmation.delete()
            print("WORKING UISERDEARILS")
            return Response(
                {
                    "message": "User created successfully.",
                    "user": UserSerializer(user).data,
                    "auth-status": "success",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print("Error in user details: " + str(e))
            return Response(
                {"message": "User created successfully", "auth-status": "success"},
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP ADD USER DETAILS }


## USER SIGN-UP GOOGLE ACCOUNT {


class SignupWithGoogleAccountView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_googleId = request.data["google_id"]
        try:
            if UserAddon.objects.filter(google_id=temp_googleId).exists():
                user = UserAddon.objects.get(google_id=temp_googleId)
                if not user.is_active:
                    return Response(
                        {
                            "message": "Google account is already linked to an blocked account.",
                            "auth-status": "failure",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                serializer = UserSerializer(user)
                return Response(
                    {
                        "message": "Welcome to studyzed",
                        "auth-status": "success",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            dummy_password = "".join(
                random.choices(string.ascii_letters + string.digits, k=12)
            )
            password = make_password(dummy_password)
            created = UserAddon.objects.create(
                email=request.data["email"],
                google_id=temp_googleId,
                role=request.data["role"],
                first_name=request.data["first_name"],
                username=request.data["username"],
                password=password,
            )
            refresh = RefreshToken.for_user(created)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            serializer = UserSerializer(created)
            print(access_token, refresh_token)
            return Response(
                {
                    "message": "Account created successfully",
                    "auth-status": "success",
                    "refresh_token": refresh_token,
                    "access_token": access_token,
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print("Exception :", e)
            return Response(
                {"message": f"Email verification failed {e}", "auth-status": "failure"},
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP GOOGLE ACCOUNT }


## USER LOGIN {


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            user = self.UserAuthenticator(request.data)
            serializer = UserSerializer(user)
            print("USER :", user)
            if user is not None and user.is_active:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                # access_token['extras'] = "adsadsdasdasdasdasdasdasdsd"
                refresh_token = str(refresh)
                print(access_token, refresh_token)

                response = Response(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": serializer.data,
                        "role": user.role,
                        "user_code": user.user_code,
                        "message": "Logged in successfully",
                        "auth-status": "success",
                    },
                    status=status.HTTP_200_OK,
                )
                print("RESPONSE :", response)
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                )
                response.set_cookie(
                    key="refresh_token", value=refresh_token, httponly=True, secure=True
                )
                return response
            elif user is not None and not user.is_active:
                return Response(
                    {"error": "User is blocked", "message": "Logged is blocked", "auth-status": "blocked"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            print("Error in login: ", str(e))
            return Response(
                {"error": "Invalid credentials", "message": str(e)}, status=status.HTTP_401_UNAUTHORIZED
            )

    def UserAuthenticator(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = UserAddon.objects.get(email=email)
            print(user, "GOTTTT")
            if user.check_password(password) and user.is_active:
                return user
            elif not user.is_active:
                print("User is Blocked")
        except UserAddon.DoesNotExist:
            print("333")
            return None


## USER LOGIN }


## USER TOCKEN CREATER{

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class CustomTokenRefreshView(TokenRefreshView):
    pass

## USER TOCKEN CREATER }


## USER FORGOTTEN PASSWORD {


class ForgotPasswordEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = UserAddon.objects.get(email=request.data["email"])
            if user is None:
                return Response(
                    {
                        "error": "Email not found, user not exisit",
                        "message": "your account not found",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not user.is_active:
                return Response(
                    {
                        "error": "User is unauthorized",
                        "message": "User is temporarly blocked, please contact the admin",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            email_task = send_forgot_password_email(user.email)
            print("EMAIL TASK :", email_task)
            if not email_task["success"]:
                print("WORKING 133")
                return Response(
                    {"error": "ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            # data = email_task
            expires_at = timezone.make_aware(
                email_task["expires_at"], timezone=ZoneInfo("UTC")
            )
            print(type(expires_at))
            # print("REDIS : ",redis_client.hgetall(user.email))
            return Response(
                {
                    "message": "Email verification success",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )

        except UserAddon.DoesNotExist:
            return Response(
                {
                    "error": "Email not found, user not exisit",
                    "message": "Email not found, user not exisit",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class ForgottenPasswordOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.data["email"]:
            redis_temp = redis_client.hgetall(request.data["email"])
            print("REDIS :", redis_temp)
            if not request.data["otp"] == redis_temp["otp"]:
                print("ERROR : ", request.data["otp"], redis_temp["otp"])
                return Response(
                    {
                        "message": "OTP is incorrect",
                        "auth-status": "failed",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                redis_temp["is_authenticated"] = True
                return Response(
                    {
                        "message": "Email verification success",
                        "auth-status": "success",
                    },
                    status=status.HTTP_200_OK,
                )


class ForgottenPasswordNewPasswordiew(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.data["email"]:
            redis_temp = redis_client.hgetall(request.data["email"])
            if not redis_temp["is_authenticated"]:
                print("ERROR : ", request.data["otp"], redis_temp["otp"])
                return Response(
                    {
                        "message": "Password cannot be changed",
                        "auth-status": "failed",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            else:
                user = UserAddon.objects.get(email=request.data["email"])
                if user.check_password(request.data["new_password"]):
                    return Response(
                        {
                            "message": "Password is already the same",
                            "auth-status": "failed",
                        },
                        status=status.HTTP_409_CONFLICT,
                    )
                user.set_password(request.data["new_password"])
                user.save()
                return Response(
                    {
                        "message": "Password changed successfully",
                        "auth-status": "success",
                    },
                    status=status.HTTP_200_OK,
                )


## USER FORGOTTEN PASSWORD }


## USER SIGN-UP SAMPLE TOKEN CHECKER {


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            referesh_token = request.data["refresh_token"] 
            token = RefreshToken(referesh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print('LOGOUT ERROR :',e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

## USER SIGN-UP SAMPLE TOKEN CHECKER }
