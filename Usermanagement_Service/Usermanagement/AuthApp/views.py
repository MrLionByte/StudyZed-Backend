import logging
import time
from zoneinfo import ZoneInfo
import redis
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from celery.result import AsyncResult
from django.utils import timezone
from django.conf import settings
from celery.exceptions import CeleryError
from .models import Email_temporary, UserAddon
from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    EmailVerificationSerializer,
    OTPVerificationSerializer,
    LoginSerializer,
    UserSerializer,
)
from .mails import (
    send_verification_email,
    send_forgot_password_email,
    resend_otp_verification_email,
)
from .utils.auth_helpers import (
    ensure_login_count_exists,
    increment_login_count,
    check_login_count,
    reset_login_count,
)

# Create your views here.

redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
logger = logging.getLogger(__name__)


## USER SIGN-UP EMAIL {


class SignupEmailProcedureView(generics.CreateAPIView):
    """_summary_

    Args:
        generics (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        temp_mail = request.data["email"]
        temp_data = Email_temporary.objects.filter(email=temp_mail).first()
        if temp_data:
            temp_data.delete()
            logger.info("Email already in use, deleted old record")

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            print(serializer.is_valid())
            email = serializer.validated_data["email"]
            email_task = send_verification_email.delay(email)
            print(email, email_task)
            result = AsyncResult(email_task.id)

            for _ in range(10):  # Max 10 retries
                if result.status == "SUCCESS":
                    break
                time.sleep(1)

            if result.status == "PENDING":
                # logger.info("Email verified Error at Pending")
                return Response(
                    {"error": "ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            data = result.get()
            expires_at = timezone.make_aware(
                data["task"]["expires_at"], timezone=ZoneInfo("UTC")
            )

            Email_temporary.objects.create(
                email=email, otp=data["task"]["otp"], expires_at=expires_at
            )

            logger.info("Email verified successfully")

            return Response(
                {
                    "message": "Email verification success",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            logger.error("Error ValueError: %s", e, exc_info=True)
            return Response(
                {
                    "message": "Email verification failed, email already in use",
                },
                status=status.HTTP_409_CONFLICT,
            )
        except CeleryError as e:
            logger.error("Celery Task Error: %s", e, exc_info=True)
            return Response(
                {
                    "message": "Background task failed",
                    "auth-status": "failure",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error("Error Exception: %s", e, exc_info=True)
            return Response(
                {
                    "message": "Email verification failed",
                    "auth-status": "failure",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP EMAIL }


## USER SIGN-UP OTP VERIFICATION {


class SignupOTPVerificationView(generics.CreateAPIView):
    """_summary_

    Args:
        generics (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            user_under_verification = Email_temporary.objects.get(
                email=request.data["email"]
            )

            user_under_verification.no_of_try += 1

            key = request.data["email"]
            redis_client.hincrby(key, "resend_count", 1)

            user_under_verification.save()
            if user_under_verification.no_of_try > 5:
                logger.error("Maximum tries exceeded", exc_info=True)
                return Response(
                    {"error": "Maximum tries exceeded."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if not serializer.is_valid():
                logger.error(
                    f"Error Invalid data: {serializer.errors}",
                    exc_info=True,
                )
                return Response(
                    {
                        "error": "Invalid data",
                        "details": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_under_verification.is_authenticated = True
            user_under_verification.save()
            logger.info("OTP verified successfully, Email is confirmed")
            return Response(
                {
                    "message": "OTP verified successfully. Email is confirmed.",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error Exception: {e}", exc_info=True)
            return Response(
                {
                    "error": f"Faied to verify OTP:, {e}",
                    "auth-status": "failed",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP OTP VERIFICATION }


## USER SIGN-UP OTP RESEND {


class SignupOTPResendView(generics.CreateAPIView):
    """_summary_

    Args:
        generics (_type_): _description_

    Returns:
        _type_: _description_
    """

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
                {
                    "message": f"OTP resend failed {e}",
                    "auth-status": "failure",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP OTP RESEND }


## USER SIGN-UP ADD USER DETAILS {


class SignupUserDetailsView(generics.CreateAPIView):
    """_summary_

    Args:
        generics (_type_): _description_

    Returns:
        _type_: _description_
    """

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
                    {
                        "error": "Invalid data",
                        "details": serializer.errors,
                    },
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
                {
                    "message": "User created successfully",
                    "auth-status": "success",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP ADD USER DETAILS }


## USER SIGN-UP GOOGLE ACCOUNT {


class SignupWithGoogleAccountView(generics.CreateAPIView):
    """_summary_

    Args:
        generics (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]

    def post(self, request):
        temp_googleId = request.data["google_id"]
        try:
            user = UserAddon.objects.filter(google_id=temp_googleId).first()
            if user:
                if not user.is_active:
                    return Response(
                        {
                            "message": "You are blocked. For any concerns please contact admin",
                            "auth-status": "blocked",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                token_serializer = CustomTokenObtainPairSerializer.get_token(user)
                access_token = str(token_serializer.access_token)  # type: ignore
                refresh_token = str(RefreshToken.for_user(user))
                serializer = UserSerializer(user)

                return Response(
                    {
                        "message": "Logged in successfully",
                        "auth-status": "success",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": serializer.data,
                        "role": user.role,
                        "user_code": user.user_code,
                    },
                    status=status.HTTP_200_OK,
                )

            created = UserAddon.objects.create(
                email=request.data["email"],
                google_id=temp_googleId,
                role=(request.data["role"]).upper(),
                first_name=request.data["first_name"],
                username=request.data["username"],
            )
            created.set_unusable_password()
            created.save()

            token_serializer = CustomTokenObtainPairSerializer.get_token(created)
            return Response(
                {
                    "message": "Account created successfully",
                    "auth-status": "created",
                    "access_token": str(token_serializer.access_token),  # type: ignore
                    "refresh_token": str(RefreshToken.for_user(created)),
                    "user": UserSerializer(created).data,
                    "role": created.role,
                    "user_code": created.user_code,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print("Exception :", e)
            return Response(
                {
                    "message": f"Email verification failed",
                    "auth-status": "failure",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


## USER SIGN-UP GOOGLE ACCOUNT }


## USER LOGIN {


class LoginView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            login_data = request.data
            email = login_data.get("email")

            if not email:
                return Response(
                    {
                        "status": "error",
                        "error": "Email is required",
                        "auth-status": "validation-failed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_email = (
                UserAddon.objects.filter(username=email)
                .values_list("email", flat=True)
                .first()
            )
            if user_email:
                login_data["email"] = user_email

            ensure_login_count_exists(email)

            if check_login_count(email):
                return Response(
                    {
                        "status": "error",
                        "message": "Too many login attempts. Please try again later.",
                        "auth-status": "locked-out",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            serializer = LoginSerializer(data=login_data)
            if serializer.is_valid():
                user = serializer.validated_data["user"]  # type: ignore

                token_serializer = CustomTokenObtainPairSerializer.get_token(user)
                access_token = str(token_serializer.access_token)  # type: ignore
                refresh_token = str(RefreshToken.for_user(user))
                reset_login_count(email)
                response = Response(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "username": user.username,
                            "role": user.role,
                        },
                        "role": user.role,
                        "user_code": user.user_code,
                        "message": "Logged in successfully",
                        "auth-status": "success",
                    },
                    status=status.HTTP_200_OK,
                )

                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                )
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                )
                return response

            increment_login_count(email)
            errors = serializer.errors
            return Response(
                {
                    "status": "error",
                    "message": "Validation failed",
                    "auth-status": errors.get("auth-status", "validation-failed"),
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error("")
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                    "auth-status": "server-error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


## USER LOGIN }


## USER TOKEN CREATE{


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


## USER TOKEN CREATE }


## USER FORGOTTEN PASSWORD {


class ForgotPasswordEmailView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """

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
    """_summary_

    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]

    def post(self, request):
        if request.data["email"]:
            redis_temp = redis_client.hgetall(request.data["email"])
            if not request.data["otp"] == redis_temp["otp"]:  # type: ignore
                return Response(
                    {
                        "message": "OTP is incorrect",
                        "auth-status": "failed",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            redis_temp["is_authenticated"] = True  # type: ignore
            return Response(
                {
                    "message": "Email verification success",
                    "auth-status": "success",
                },
                status=status.HTTP_200_OK,
            )


class ForgottenPasswordNewPassword(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if request.data["email"]:
            redis_temp = redis_client.hgetall(request.data["email"])
            if not redis_temp["is_authenticated"]:  # type: ignore
                return Response(
                    {
                        "message": "Password cannot be changed",
                        "auth-status": "failed",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

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
        return Response(
            {
                "message": "Enter a valid email",
                "auth-status": "failed",
            },
            status=status.HTTP_200_OK,
        )


## USER FORGOTTEN PASSWORD }


## USER SIGN-UP SAMPLE TOKEN CHECKER {


class LogoutView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_

    Returns:
        _type_: _description_
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("LOGOUT ERROR :", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


## USER SIGN-UP SAMPLE TOKEN CHECKER }
