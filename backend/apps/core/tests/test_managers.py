"""
Tests for custom managers (TenantManager, TenantManagerUnscoped).
"""

import pytest
from django.test import TestCase
from apps.core.threadlocals import set_current_business, clear_current_business
from apps.core.models import Business
from apps.resources.models import Resource  # Example TenantModel


@pytest.mark.django_db
class TenantManagerTests(TestCase):
    """Test TenantManager automatic business filtering."""

    def setUp(self):
        """Create test businesses and resources."""
        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )
        self.business2 = Business.objects.create(
            name="Widget Co",
            subdomain="widgets"
        )

        # Create resources for each business
        self.resource1_biz1 = Resource.objects.create(
            business=self.business1,
            name="Resource 1 Biz 1",
            type="STAFF"
        )
        self.resource2_biz1 = Resource.objects.create(
            business=self.business1,
            name="Resource 2 Biz 1",
            type="ROOM"
        )
        self.resource1_biz2 = Resource.objects.create(
            business=self.business2,
            name="Resource 1 Biz 2",
            type="STAFF"
        )

    def tearDown(self):
        """Clear thread-local after each test."""
        clear_current_business()

    def test_queryset_filtered_by_current_business(self):
        """Test that queries are automatically filtered by current business."""
        # Set business1 as current
        set_current_business(self.business1)

        # Query should only return business1's resources
        resources = Resource.objects.all()
        self.assertEqual(resources.count(), 2)
        self.assertIn(self.resource1_biz1, resources)
        self.assertIn(self.resource2_biz1, resources)
        self.assertNotIn(self.resource1_biz2, resources)

        # Switch to business2
        set_current_business(self.business2)

        # Query should only return business2's resources
        resources = Resource.objects.all()
        self.assertEqual(resources.count(), 1)
        self.assertIn(self.resource1_biz2, resources)
        self.assertNotIn(self.resource1_biz1, resources)

    def test_queryset_unfiltered_when_no_business(self):
        """Test that queries are unfiltered when no business is set."""
        # No business set
        clear_current_business()

        # Query should return all resources
        resources = Resource.objects.all()
        self.assertEqual(resources.count(), 3)

    def test_objects_unscoped_bypasses_filtering(self):
        """Test that objects_unscoped returns all objects across businesses."""
        # Set business1 as current
        set_current_business(self.business1)

        # objects_unscoped should return all resources
        all_resources = Resource.objects_unscoped.all()
        self.assertEqual(all_resources.count(), 3)

        # objects (default) should only return business1's resources
        filtered_resources = Resource.objects.all()
        self.assertEqual(filtered_resources.count(), 2)

    def test_filter_chains_with_tenant_manager(self):
        """Test that additional filters work correctly with TenantManager."""
        set_current_business(self.business1)

        # Filter by type within current business
        staff_resources = Resource.objects.filter(type="STAFF")
        self.assertEqual(staff_resources.count(), 1)
        self.assertEqual(staff_resources.first().name, "Resource 1 Biz 1")

        room_resources = Resource.objects.filter(type="ROOM")
        self.assertEqual(room_resources.count(), 1)
        self.assertEqual(room_resources.first().name, "Resource 2 Biz 1")

    def test_get_with_tenant_manager(self):
        """Test that get() respects business filtering."""
        set_current_business(self.business1)

        # Should find resource in current business
        resource = Resource.objects.get(name="Resource 1 Biz 1")
        self.assertEqual(resource, self.resource1_biz1)

        # Should not find resource in different business
        with self.assertRaises(Resource.DoesNotExist):
            Resource.objects.get(name="Resource 1 Biz 2")
