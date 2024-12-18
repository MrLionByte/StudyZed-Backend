import redis
import json
from .models import Email_temporary, UserAddon
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from rest_framework.views import APIView
from .mails import send_verification_email
from django.utils.timezone import now
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from celery.result import AsyncResult


# Create your views here.

redis_client = redis.StrictRedis(host='redis', port=6379, db=0,
                                 decode_responses=True)

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
            print("RESULT :", result.get(),"  :::: " ,result.result)
            if result.status == "PENDING":
                print("WORKING 133")
                return Response(
                    {"error": "ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            print("RESULT :", result.get(),"  :::: " ,result.result)
            # new_temp_data = Email_temporary.objects.create(
            #     email=email,otp=email_status['otp'],expires_at=email_status['expires_at'])
            # print("TEMP :", new_temp_data)
            # print("WORKING 1555")
            return Response({
                "message": "Email verification failed",
                "auth-status": "success",},
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

        # print(f"DATA IN SESSION AFTER TRY : {request.session['validationsteps']}")
        # request.session["validationsteps"]['no_of_try'] = int(request.session["validationsteps"].get('no_of_try')) + 1
        # request.session.modified = True
        # print(f"DATA IN SESSION AFTER TRY : {request.session['validationsteps']}")
        serializer = self.get_serializer(data=request.data)
        try:
            user_under_verification = Email_temporary.objects.get(
                email=request.data["email"]
            )
            print("user_under_verification :", user_under_verification)
            user_under_verification.no_of_try += 1
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
    serializer_class = OTPVerificationSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        try:
            user_under_verification = Email_temporary.objects.get(
                email=request.data["email"]
            )

            if not serializer.is_valid():
                print("Error", serializer.errors)
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


## USER LOGIN {


class LoginView(APIView):
    permission_classes = [AllowAny]
    print("WORKING")

    def post(self, request, *args, **kwargs):
        try:
            user = self.UserAuthenticator(request.data)
            # print("PARAMS :", request.GET.get('login_type'))
            serializer = UserSerializer(user)
            print("USER :", user)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                print(access_token, refresh_token)

                response = Response(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": serializer.data,
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
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            print("Error in login: ", str(e))
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    def UserAuthenticator(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = UserAddon.objects.get(email=email)
            print(user, "GOTTTT")
            if user.check_password(password):
                print("111")
                return user
            else:
                print("222")
                return None
        except UserAddon.DoesNotExist:
            print("333")
            return None


## USER LOGIN }


## USER FORGOTTEN PASSWORD {


class ForgottenPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def forgot_password(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = serializer.validated_data["email"]
        user = UserAddon.objects.get(email=email)

        
        
        return Response({"reset_url": f"{rest_url}"},
                        status=status.HTTP_200_OK)

    def UserAuthenticator(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = UserAddon.objects.get(email=email)
            print(user, "GOTTTT")
            if user.check_password(password):
                print("111")
                return user
            else:
                print("222")
                return None
        except UserAddon.DoesNotExist:
            print("333")
            return None


## USER FORGOTTEN PASSWORD }


## USER SIGN-UP SAMPLE TOKEN CHECKER {


class SampleRequestChecker(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data, "WORKINGGG")
        return Response({"message": "Request accepted"}, status=status.HTTP_200_OK)


## USER SIGN-UP SAMPLE TOKEN CHECKER }

