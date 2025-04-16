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
from AuthApp.mails import (
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
from .utils.responses import api_response

# Create your views here.

redis_client = redis.StrictRedis(
    host=str(settings.REDIS_HOST), port=settings.REDIS_PORT, db=0, decode_responses=True
)
logger = logging.getLogger(__name__)

## USER SIGN-UP EMAIL {


class SignupEmailProcedureView(generics.CreateAPIView):
    """
    Handles email verification during the signup process.

    Args:
        request (Request): The HTTP/HTTPS request containing the email to be verified.

    Returns:
        _type_: Response: A response indicating whether the email verification was successful or failed.
    """

    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            temp_mail = request.data["email"]
            temp_data = Email_temporary.objects.filter(email=temp_mail).first()
            if temp_data:
                temp_data.delete()
                logger.info("Email already in use, deleted old record")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data["email"]
            
            retry_count = 0
            max_retries = 3
            email_task = None
            
            while retry_count < max_retries:
                try:
                    email_task = send_verification_email.apply_async(args=[email])
                    logger.info(f"Task registration successful on attempt {retry_count+1}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        return Response(
                            {"error": "Service unavailable - task registration failed"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
                    time.sleep(1)
            
            if email_task:
                result = AsyncResult(email_task.id)
                success = False
                
                for attempt in range(10):  # Max 10 retries
                    logger.info(f"Waiting for task completion, attempt {attempt+1}")
                    if result.status == "SUCCESS":
                        success = True
                        break
                    time.sleep(1)
            
                if not success:
                    logger.error("Task execution timed out or failed")
                    return Response(
                        {"error": "Task execution timed out"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                try:
                    data = result.get(timeout=3)
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
                except Exception as e:
                    logger.error(f"Error processing task result: {str(e)}", exc_info=True)
                    return Response(
                        {"error": "Failed to process task result"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(
                    {"error": "Failed to create task"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    """Handles otp verification process during signup.

    Args:
        request (Request): The HTTP/HTTPS request containing the otp to be verified.

    Returns:
        Response: A response indicating whether the otp verification was successful or failed.
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
    """
        Handles OTP resend during the signup process if the OTP has expired.

    Args:
        request (Request): The HTTP request containing the email for which OTP should be resent.

    Returns:
        Response: A response indicating whether the OTP resend was successful or failed.
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
            # email_task = resend_otp_verification_email.delay(email)
            email_task = resend_otp_verification_email.apply_async(args=[email])
            
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
    """
    Handles user registration after email verification.

    Args:
        request (Request): The HTTP request containing user details for signup.

    Returns:
        Response: A response indicating whether the user was successfully created or if an error occurred.
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
    """
    Handles both user signup and login using a Google account.
    If the user exists, logs them in. If not, creates a new account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            google_id = request.data.get("google_id")
            email = request.data.get("email")
            
            if not google_id or not email:
                return Response(
                    {
                        "message": "Google ID and email are required",
                        "auth-status": "validation-failed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            user = UserAddon.objects.filter(google_id=google_id).first()
            
            if not user:
                email_exists = UserAddon.objects.filter(email=email).exists()
                if email_exists:
                    return Response(
                        {
                            "message": "Email already in use with a different account",
                            "auth-status": "email-exists",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                role = request.data.get("role")
                if not role:
                    return Response(
                        {
                            "message": "Role is required for new accounts",
                            "auth-status": "role-required",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                user = UserAddon.objects.create(
                    email=email,
                    google_id=google_id,
                    role=role.upper(),
                    first_name=request.data.get("first_name", ""),
                    last_name=request.data.get("last_name", ""),
                    username=request.data.get("username", "").lower(),
                )
                user.set_unusable_password()
                user.save()
                
                auth_status = "created"
                message = "Account created successfully"
            else:
                if not user.is_active:
                    return Response(
                        {
                            "message": "Your account is blocked. Please contact admin for assistance",
                            "auth-status": "blocked",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                
                auth_status = "success"
                message = "Logged in successfully"
            
            refresh = RefreshToken.for_user(user)
            token_serializer = CustomTokenObtainPairSerializer.get_token(user)
            
            return Response(
                {
                    "message": message,
                    "auth-status": auth_status,
                    "access_token": str(token_serializer.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                    "role": user.role,
                    "user_code": user.user_code,
                },
                status=status.HTTP_200_OK,
            )
                
        except Exception as e:
            print(f"Google Auth Exception: {e}")
            return Response(
                {
                    "message": "Authentication failed",
                    "auth-status": "failure",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


## USER SIGN-UP GOOGLE ACCOUNT }


## USER LOGIN {


class LoginView(APIView):
    """
    Handles user login, including validation, authentication, and token generation.

    Args:
        request (Request): The HTTP request containing login credentials.

    Returns:
        Response: A response with authentication tokens if login is successful,
        or an error message if validation fails or the user is locked out.
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
            logger.error(f"Error Exception: {e}", exc_info=True)
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
    """
    Custom views for obtaining jwt token.

    CustomTokenObtainPairView:
        Uses a custom serializer to generate access and refresh tokens.
    """

    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom views for refreshing JWT tokens.

    CustomTokenRefreshView:
        Uses a custom serializer to refresh expired access tokens.
    """

    serializer_class = CustomTokenRefreshSerializer


## USER TOKEN CREATE }


## USER FORGOTTEN PASSWORD {


class ForgotPasswordEmailView(APIView):
    """
    Handles the process of initiating a password reset by sending a reset email.

    Args:
        APIView (APIView): Inherits from Django REST framework's APIView.

    Returns:
        Response: A response indicating whether the email was sent successfully or failed.
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
    """
    Handles OTP verification during the password reset process.

    Args:
        APIView (APIView): Inherits from Django REST framework's APIView.

    Returns:
        Response: A response indicating whether the OTP verification was successful or failed.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"error": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        redis_temp = redis_client.hgetall(email)

        if not redis_temp or "otp" not in redis_temp:
            return Response(
                {"error": "OTP expired or invalid"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if otp != redis_temp["otp"]:
            return Response(
                {"message": "OTP is incorrect", "auth-status": "failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        redis_temp["is_authenticated"] = True  # type: ignore
        redis_client.hmset(email, redis_temp)

        return Response(
            {
                "message": "Email verification success",
                "auth-status": "success",
            },
            status=status.HTTP_200_OK,
        )


class ForgottenPasswordNewPassword(APIView):
    """
    Handles setting a new password after OTP verification.

    Args:
        APIView (APIView): Inherits from Django REST framework's APIView.

    Returns:
        Response: A response indicating whether the password change was successful or failed.
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
    """
    Handles user logout by blacklisting the refresh token.

    Args:
        APIView (APIView): Inherits from Django REST framework's APIView.

    Returns:
        Response: A response indicating whether the logout was successful or failed.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


## USER SIGN-UP SAMPLE TOKEN CHECKER }
