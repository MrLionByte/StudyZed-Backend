from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    # USER SIGN-UP
    path("user-email/", SignupEmailProcedureView.as_view(), name="email_verification"),
    path("verify-otp/", SignupOTPVerificationView.as_view(), name="otp_verification"),
    path("resend-otp/", SignupOTPResendView.as_view(), name="otp_resend"),
    path("user-details/", SignupUserDetailsView.as_view(), name="user_signup"),
    
    path("login/google-account/", SignupWithGoogleAccountView.as_view(), name="login_google_account"),
    
    
    # DRF TOKEN ACCESS & REFRESH
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('user/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # LOGIN & FORGOT PASSWORD
    path("login/", LoginView.as_view(), name="login"),
    path("login/forgot-password/", ForgotPasswordEmailView.as_view(), name="forgot_password_email"),
    path("login/forgot-password/otp-verify/", ForgottenPasswordOTPView.as_view(), name="forgot_password_otp"),
    path("login/forgot-password/change-password/", ForgottenPasswordNewPasswordiew.as_view(), name="forgot_password_new_password"),
    
    
    path("sample-request/", SampleRequestChecker.as_view(), name="sample"),
    
]
