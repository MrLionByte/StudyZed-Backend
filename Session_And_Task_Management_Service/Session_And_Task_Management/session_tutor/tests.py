from django.test import TestCase
from django.utils import timezone
from .models import Session
import uuid
from datetime import timedelta

class SessionModelTest(TestCase):
    """Tests for Session model"""

    def setUp(self):
        self.session = Session.objects.create(
            tutor_code="TUTOR1233",
            session_name="Testing Masterclass",
            session_grade="10",
            session_duration=Session.SubscriptionType.THREE_MONTHS,
            session_discription="A simple test course",
            is_paid=True,
            is_active=True,
            image="uploads/session/test_image.jpg",
            start_date=timezone.now()
        )

    def test_session_creation(self):
        """Ensure the Session instance is created properly"""
        self.assertEqual(self.session.tutor_code, "TUTOR1233")
        self.assertEqual(self.session.session_name, "Testing Masterclass")
        self.assertEqual(self.session.session_grade, "10")
        self.assertEqual(self.session.session_duration, 3)
        self.assertEqual(self.session.session_discription, "A simple test course")
        self.assertTrue(self.session.is_paid)
        self.assertTrue(self.session.is_active)
        self.assertEqual(self.session.image, "uploads/session/test_image.jpg")
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.updated_at)
        self.assertIsNotNone(self.session.start_date)

    def test_session_code_generation(self):
        """Check if session_code is auto-generated correctly"""
        self.assertTrue(self.session.session_code)
        self.assertTrue(len(self.session.session_code) <= 150)
        self.assertTrue('-' in self.session.session_code)
        name_portion = ''.join(filter(str.isalnum, self.session.session_name))[:5].upper()
        self.assertTrue(self.session.session_code.startswith(f"{name_portion}-"))

    def test_session_code_uniqueness(self):
        """Ensure session_code is unique"""
        session2 = Session.objects.create(
            tutor_code="TUTOR456",
            session_name="Science Workshop",
            session_duration=Session.SubscriptionType.ONE_MONTH
        )
        self.assertNotEqual(self.session.session_code, session2.session_code)

    def test_subscription_type_choices(self):
        """Ensure subscription type is set correctly"""
        self.assertEqual(self.session.session_duration, Session.SubscriptionType.THREE_MONTHS)
        self.assertIn(self.session.session_duration, [choice[0] for choice in Session.SubscriptionType.choices])

    def test_string_representation(self):
        """Check if the __str__ method returns correct values"""
        self.assertEqual(str(self.session), "Math Masterclass => TUTOR123")

    def test_auto_timestamps(self):
        """Verify created_at and updated_at are set automatically"""
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.updated_at)
        self.assertTrue(self.session.updated_at >= self.session.created_at)

    def test_blank_fields(self):
        """Test that optional fields can be blank"""
        session = Session.objects.create(
            tutor_code="TUTOR789",
            session_name="History Class",
            session_duration=Session.SubscriptionType.SIX_MONTHS
        )
        self.assertEqual(session.session_grade, "")
        self.assertEqual(session.session_discription, "")
        self.assertIsNone(session.start_date)