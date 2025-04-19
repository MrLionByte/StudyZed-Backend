from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from AuthApp.models import UserAddon, Email_temporary
from django.utils import timezone
from unittest.mock import patch

class ForgotPasswordEmailViewTest(TestCase):
    """Test the ForgotPasswordEmailView"""

    def setUp(self):
        self.client = APIClient()
        self.user = UserAddon.objects.create(email="test@example.com", username="testuser", role="STUDENT")
    
    def test_send_forgot_password_email(self):
        """Ensure the forgot password email is sent"""
        response = self.client.post(reverse("forgot_password_email"), {"email": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["auth-status"], "success")

    def test_send_email_to_nonexistent_user(self):
        """Ensure sending an email to a non-existent user fails"""
        response = self.client.post(reverse("forgot_password_email"), {"email": "notfound@example.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ForgottenPasswordOTPViewTest(TestCase):
    """Test OTP verification for forgotten password"""

    def setUp(self):
        self.client = APIClient()
        self.email = "test@example.com"
        self.otp = "123456"
        
        Email_temporary.objects.create(email=self.email, otp=self.otp, expires_at=timezone.now())

    @patch("AuthApp.views.redis_client.get") 
    def test_correct_otp(self, mock_redis_get):
        """Ensure OTP verification works"""
        mock_redis_get.return_value = {"otp": self.otp}
        
        response = self.client.post(reverse("forgot_password_otp"), 
                               {"email": self.email, "otp": self.otp})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("AuthApp.views.redis_client.get")  
    def test_incorrect_otp(self, mock_redis_get):
        """Ensure incorrect OTP fails"""
        mock_redis_get.return_value = {"otp": self.otp}
        response = self.client.post(reverse("forgot_password_otp"), 
                               {"email": self.email, "otp": "999999"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class LoginViewTest(TestCase):
    """Test user login"""

    def setUp(self):
        self.client = APIClient()
        self.user = UserAddon.objects.create(username="testuser", email="test@example.com", role="STUDENT")
        self.user.set_password("testpassword")
        self.user.save()

    def test_login_success(self):
        """Ensure valid login works"""
        response = self.client.post(reverse("login"), {"email": "test@example.com", "password": "testpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_login_failure(self):
        """Ensure invalid login fails"""
        response = self.client.post(reverse("login"), {"email": "test@example.com", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
