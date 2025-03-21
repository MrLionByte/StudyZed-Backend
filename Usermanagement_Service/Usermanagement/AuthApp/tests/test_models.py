from django.test import TestCase
from django.utils import timezone
from AuthApp.models import Email_temporary, UserAddon, Profile
import uuid

# Create your tests here.


class EmailTestCase(TestCase):
    """Test for Email_temporary model"""
    
    def setUp(self):
        self.temp_email = Email_temporary.objects.create(
            email='test@example.com',
            otp='123456',
            expires_at=timezone.now(),

        )
    
    def test_email_temporary_creation(self):
        """Ensure the Email_temporary instance is created properly"""
        self.assertEqual(self.temp_email.email, "test@example.com")
        self.assertEqual(self.temp_email.otp, "123456")
        self.assertEqual(self.temp_email.no_of_try, 0)
        self.assertFalse(self.temp_email.is_authenticated)

    def test_email_temporary_string_representation(self):
        """Check if the __str__ method returns correct values"""
        self.assertEqual(str(self.temp_email), "('test@example.com', '123456')")

class UserAddonModelTest(TestCase):
    """Tests for UserAddon model"""

    def setUp(self):
        self.user = UserAddon.objects.create(
            username="testuser",
            email="user@example.com",
            role="STUDENT",
        )

    def test_user_code_generation(self):
        """Check if user_code is auto-generated"""
        self.assertTrue(self.user.user_code)
        self.assertTrue(self.user.user_code.startswith("TESTU-"))

    def test_role_choices(self):
        """Ensure role is set correctly"""
        self.assertEqual(self.user.role, "STUDENT")

class ProfileModelTest(TestCase):
    """Tests for Profile model"""

    def setUp(self):
        self.user = UserAddon.objects.create(username="user1", email="user1@example.com", role="TUTOR")
        self.profile = Profile.objects.create(user=self.user, phone="1234567890")

    def test_profile_creation(self):
        """Ensure the profile is linked to a user"""
        self.assertEqual(self.profile.user.username, "user1")
        self.assertEqual(self.profile.phone, "1234567890")