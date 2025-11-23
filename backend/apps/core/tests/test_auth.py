"""
Tests for BusinessScopedAuthBackend (multi-tenant authentication).
"""

import pytest
from django.test import TestCase, RequestFactory
from apps.core.auth import BusinessScopedAuthBackend
from apps.core.models import Business, User


@pytest.mark.django_db
class BusinessScopedAuthBackendTests(TestCase):
    """Test business-scoped authentication."""

    def setUp(self):
        """Create test businesses and users."""
        self.factory = RequestFactory()
        self.backend = BusinessScopedAuthBackend()

        # Create businesses
        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )
        self.business2 = Business.objects.create(
            name="Widget Co",
            subdomain="widgets"
        )

        # Create users with same email in different businesses
        self.user1_biz1 = User.objects.create_user(
            username="john_acme",
            email="john@example.com",
            password="password123",
            business=self.business1,
            role="owner"
        )
        self.user1_biz2 = User.objects.create_user(
            username="john_widgets",
            email="john@example.com",
            password="differentpass456",
            business=self.business2,
            role="manager"
        )

        # Create platform user (no business)
        self.platform_user = User.objects.create_user(
            username="platform_admin",
            email="admin@smoothschedule.com",
            password="platformpass789",
            business=None,
            role="superuser"
        )

    def test_authenticate_with_correct_business(self):
        """Test authentication with correct email + password + business."""
        request = self.factory.post("/login/")
        request.business = self.business1

        user = self.backend.authenticate(
            request=request,
            username="john@example.com",
            password="password123"
        )

        self.assertEqual(user, self.user1_biz1)

    def test_authenticate_same_email_different_business(self):
        """Test that same email authenticates to different user in different business."""
        # Authenticate to business1
        request1 = self.factory.post("/login/")
        request1.business = self.business1

        user1 = self.backend.authenticate(
            request=request1,
            username="john@example.com",
            password="password123"
        )
        self.assertEqual(user1, self.user1_biz1)

        # Authenticate to business2 (same email, different password)
        request2 = self.factory.post("/login/")
        request2.business = self.business2

        user2 = self.backend.authenticate(
            request=request2,
            username="john@example.com",
            password="differentpass456"
        )
        self.assertEqual(user2, self.user1_biz2)
        self.assertNotEqual(user1, user2)

    def test_authenticate_wrong_password(self):
        """Test authentication fails with wrong password."""
        request = self.factory.post("/login/")
        request.business = self.business1

        user = self.backend.authenticate(
            request=request,
            username="john@example.com",
            password="wrongpassword"
        )

        self.assertIsNone(user)

    def test_authenticate_user_not_in_business(self):
        """Test that user from business1 cannot authenticate to business2."""
        request = self.factory.post("/login/")
        request.business = self.business2

        # Try business1 user's password on business2
        user = self.backend.authenticate(
            request=request,
            username="john@example.com",
            password="password123"  # business1's password
        )

        # Should fail or authenticate to different user
        if user is not None:
            self.assertEqual(user, self.user1_biz2)
            self.assertNotEqual(user, self.user1_biz1)

    def test_authenticate_platform_user(self):
        """Test authentication for platform users (no business)."""
        request = self.factory.post("/login/")
        request.business = None  # Platform request

        user = self.backend.authenticate(
            request=request,
            username="admin@smoothschedule.com",
            password="platformpass789"
        )

        self.assertEqual(user, self.platform_user)

    def test_authenticate_missing_username(self):
        """Test authentication fails when username is missing."""
        request = self.factory.post("/login/")
        request.business = self.business1

        user = self.backend.authenticate(
            request=request,
            username=None,
            password="password123"
        )

        self.assertIsNone(user)

    def test_authenticate_missing_password(self):
        """Test authentication fails when password is missing."""
        request = self.factory.post("/login/")
        request.business = self.business1

        user = self.backend.authenticate(
            request=request,
            username="john@example.com",
            password=None
        )

        self.assertIsNone(user)

    def test_get_user_by_id(self):
        """Test retrieving user by ID."""
        user = self.backend.get_user(self.user1_biz1.id)
        self.assertEqual(user, self.user1_biz1)

    def test_get_user_nonexistent_id(self):
        """Test retrieving nonexistent user returns None."""
        import uuid
        user = self.backend.get_user(uuid.uuid4())
        self.assertIsNone(user)
