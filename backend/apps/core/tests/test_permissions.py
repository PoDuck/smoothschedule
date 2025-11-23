"""
Tests for role-based permission classes.
"""

import pytest
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from apps.core.models import Business, User
from apps.core.permissions import (
    IsOwnerOrManager,
    IsOwnerOnly,
    IsStaffOrHigher,
    ReadOnly,
    CustomerCanViewOwnData,
    StaffCanModifyOwnData,
    OwnerOrManagerCanWrite,
    PlatformAdminOnly,
)


class MockView:
    """Mock view for testing permissions."""
    pass


class MockObject:
    """Mock object for testing object-level permissions."""

    def __init__(self, user=None, customer=None):
        self.user = user
        self.customer = customer


@pytest.mark.django_db
class PermissionTests(TestCase):
    """Test role-based permissions."""

    def setUp(self):
        """Create test users and request factory."""
        self.factory = APIRequestFactory()
        self.view = MockView()

        # Create business
        self.business = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )

        # Create users with different roles
        self.superuser = User.objects.create_user(
            username="superuser",
            email="super@platform.com",
            password="pass123",
            business=None,
            role="superuser"
        )

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@acme.com",
            password="pass123",
            business=self.business,
            role="owner"
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@acme.com",
            password="pass123",
            business=self.business,
            role="manager"
        )

        self.staff = User.objects.create_user(
            username="staff",
            email="staff@acme.com",
            password="pass123",
            business=self.business,
            role="staff"
        )

        self.customer = User.objects.create_user(
            username="customer",
            email="customer@acme.com",
            password="pass123",
            business=self.business,
            role="customer"
        )

    def test_is_owner_or_manager(self):
        """Test IsOwnerOrManager permission."""
        permission = IsOwnerOrManager()

        # Create GET request
        request = self.factory.get("/")

        # Owner should have permission
        request.user = self.owner
        self.assertTrue(permission.has_permission(request, self.view))

        # Manager should have permission
        request.user = self.manager
        self.assertTrue(permission.has_permission(request, self.view))

        # Superuser should have permission
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, self.view))

        # Staff should NOT have permission
        request.user = self.staff
        self.assertFalse(permission.has_permission(request, self.view))

        # Customer should NOT have permission
        request.user = self.customer
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_owner_only(self):
        """Test IsOwnerOnly permission."""
        permission = IsOwnerOnly()
        request = self.factory.get("/")

        # Owner should have permission
        request.user = self.owner
        self.assertTrue(permission.has_permission(request, self.view))

        # Superuser should have permission
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, self.view))

        # Manager should NOT have permission
        request.user = self.manager
        self.assertFalse(permission.has_permission(request, self.view))

        # Staff should NOT have permission
        request.user = self.staff
        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_staff_or_higher(self):
        """Test IsStaffOrHigher permission."""
        permission = IsStaffOrHigher()
        request = self.factory.get("/")

        # Owner, manager, staff should have permission
        for user in [self.owner, self.manager, self.staff, self.superuser]:
            request.user = user
            self.assertTrue(permission.has_permission(request, self.view))

        # Customer should NOT have permission
        request.user = self.customer
        self.assertFalse(permission.has_permission(request, self.view))

    def test_read_only(self):
        """Test ReadOnly permission."""
        permission = ReadOnly()

        # GET request should be allowed
        request = self.factory.get("/")
        self.assertTrue(permission.has_permission(request, self.view))

        # POST request should be denied
        request = self.factory.post("/")
        self.assertFalse(permission.has_permission(request, self.view))

        # PUT request should be denied
        request = self.factory.put("/")
        self.assertFalse(permission.has_permission(request, self.view))

        # DELETE request should be denied
        request = self.factory.delete("/")
        self.assertFalse(permission.has_permission(request, self.view))

    def test_customer_can_view_own_data(self):
        """Test CustomerCanViewOwnData permission."""
        permission = CustomerCanViewOwnData()

        # Create mock object owned by customer
        obj = MockObject(user=self.customer)

        request = self.factory.get("/")

        # Owner can view any object
        request.user = self.owner
        self.assertTrue(permission.has_object_permission(request, self.view, obj))

        # Manager can view any object
        request.user = self.manager
        self.assertTrue(permission.has_object_permission(request, self.view, obj))

        # Customer can view their own data
        request.user = self.customer
        self.assertTrue(permission.has_object_permission(request, self.view, obj))

        # Different customer cannot view
        other_customer = User.objects.create_user(
            username="other_customer",
            email="other@acme.com",
            password="pass123",
            business=self.business,
            role="customer"
        )
        request.user = other_customer
        self.assertFalse(permission.has_object_permission(request, self.view, obj))

    def test_owner_or_manager_can_write(self):
        """Test OwnerOrManagerCanWrite permission."""
        permission = OwnerOrManagerCanWrite()

        # GET request - everyone authenticated can read
        get_request = self.factory.get("/")

        for user in [self.owner, self.manager, self.staff, self.customer]:
            get_request.user = user
            self.assertTrue(permission.has_permission(get_request, self.view))

        # POST request - only owner/manager can write
        post_request = self.factory.post("/")

        # Owner and manager can write
        for user in [self.owner, self.manager, self.superuser]:
            post_request.user = user
            self.assertTrue(permission.has_permission(post_request, self.view))

        # Staff and customer cannot write
        for user in [self.staff, self.customer]:
            post_request.user = user
            self.assertFalse(permission.has_permission(post_request, self.view))

    def test_platform_admin_only(self):
        """Test PlatformAdminOnly permission."""
        permission = PlatformAdminOnly()
        request = self.factory.get("/")

        # Superuser should have permission
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, self.view))

        # Business users should NOT have permission
        for user in [self.owner, self.manager, self.staff, self.customer]:
            request.user = user
            self.assertFalse(permission.has_permission(request, self.view))

    def test_unauthenticated_user_denied(self):
        """Test that unauthenticated users are denied by all permissions."""
        from django.contrib.auth.models import AnonymousUser

        permissions_to_test = [
            IsOwnerOrManager(),
            IsOwnerOnly(),
            IsStaffOrHigher(),
            OwnerOrManagerCanWrite(),
            PlatformAdminOnly(),
        ]

        request = self.factory.get("/")
        request.user = AnonymousUser()

        for permission in permissions_to_test:
            self.assertFalse(
                permission.has_permission(request, self.view),
                f"{permission.__class__.__name__} should deny anonymous users"
            )
