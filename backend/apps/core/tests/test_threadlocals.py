"""
Tests for thread-local storage functionality.
"""

import pytest
from django.test import TestCase
from apps.core.threadlocals import (
    set_current_business,
    get_current_business,
    clear_current_business,
)
from apps.core.models import Business


@pytest.mark.django_db
class ThreadLocalTests(TestCase):
    """Test thread-local storage for multi-tenancy."""

    def setUp(self):
        """Create test businesses."""
        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )
        self.business2 = Business.objects.create(
            name="Widget Co",
            subdomain="widgets"
        )

    def tearDown(self):
        """Clear thread-local after each test."""
        clear_current_business()

    def test_set_and_get_current_business(self):
        """Test setting and getting current business."""
        # Initially, no business should be set
        self.assertIsNone(get_current_business())

        # Set business1
        set_current_business(self.business1)
        self.assertEqual(get_current_business(), self.business1)

        # Set business2
        set_current_business(self.business2)
        self.assertEqual(get_current_business(), self.business2)

    def test_clear_current_business(self):
        """Test clearing current business."""
        set_current_business(self.business1)
        self.assertEqual(get_current_business(), self.business1)

        clear_current_business()
        self.assertIsNone(get_current_business())

    def test_set_none_business(self):
        """Test setting business to None (platform requests)."""
        set_current_business(self.business1)
        self.assertIsNotNone(get_current_business())

        set_current_business(None)
        self.assertIsNone(get_current_business())
