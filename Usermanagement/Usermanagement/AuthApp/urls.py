from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (SignupEmailProcedureView, SignupOTPVerificationView,
                    LoginView, SignupUserDetailsView, SampleRequestChecker,
                    )

urlpatterns = [
    path("user-email/", SignupEmailProcedureView.as_view(), name="email_verification"),
    path("verify-otp/", SignupOTPVerificationView.as_view(), name="otp_verification"),
    path("user-details/", SignupUserDetailsView.as_view(), name="user_signup"),
    
    # DRF TOKEN ACCESS & REFRESH
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('user/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
    path("login/", LoginView.as_view(), name="login"),
    path("login/forgot-password/", LoginView.as_view(), name="forgot_password"),
    
    path("sample-request/", SampleRequestChecker.as_view(), name="sample"),
    
]
