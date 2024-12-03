from django.urls import path
from .views import SignupEmailProcedureView, SignupOTPVerificationView, UploadProfile, LoginView, SignupUserDetailsView

urlpatterns = [
    path("user-email/", SignupEmailProcedureView.as_view(), name="email_verification"),
    path("verify-otp/", SignupOTPVerificationView.as_view(), name="otp_verification"),
    path("user-details/", SignupUserDetailsView.as_view(), name="user_signup"),\
        
    path("upload-profile/", UploadProfile.as_view(), name="upload_profile"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/forgot-password/", LoginView.as_view(), name="forgot_password"),
    
    
]
