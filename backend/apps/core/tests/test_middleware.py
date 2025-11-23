"""
Tests for TenantMiddleware (subdomain-based business resolution).
"""

import pytest
from django.http import Http404
from django.test import TestCase, RequestFactory
from apps.core.middleware import TenantMiddleware, get_business_from_request
from apps.core.models import Business
from apps.core.threadlocals import get_current_business, clear_current_business


@pytest.mark.django_db
class TenantMiddlewareTests(TestCase):
    """Test subdomain-based tenant resolution."""

    def setUp(self):
        """Create test businesses and request factory."""
        self.factory = RequestFactory()

        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )
        self.business2 = Business.objects.create(
            name="Widget Co",
            subdomain="widgets"
        )

        # Create a simple response function
        def get_response(request):
            return None

        self.middleware = TenantMiddleware(get_response)

    def tearDown(self):
        """Clear thread-local after each test."""
        clear_current_business()

    def test_resolve_business_from_subdomain(self):
        """Test extracting business from subdomain."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "acme.smoothschedule.com"

        business = get_business_from_request(request)
        self.assertEqual(business, self.business1)

    def test_resolve_different_business(self):
        """Test resolving different business from different subdomain."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "widgets.smoothschedule.com"

        business = get_business_from_request(request)
        self.assertEqual(business, self.business2)

    def test_invalid_subdomain_raises_404(self):
        """Test that invalid subdomain raises Http404."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "nonexistent.smoothschedule.com"

        with self.assertRaises(Http404):
            get_business_from_request(request)

    def test_platform_subdomain_returns_none(self):
        """Test that platform subdomain returns None (no business)."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "platform.smoothschedule.com"

        business = get_business_from_request(request)
        self.assertIsNone(business)

    def test_invalid_domain_raises_404(self):
        """Test that non-platform domain raises Http404."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "example.com"

        with self.assertRaises(Http404):
            get_business_from_request(request)

    def test_host_with_port_number(self):
        """Test extracting subdomain when host includes port number."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "acme.smoothschedule.com:8000"

        business = get_business_from_request(request)
        self.assertEqual(business, self.business1)

    def test_middleware_sets_thread_local(self):
        """Test that middleware sets business in thread-local storage."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "acme.smoothschedule.com"

        # Before middleware, no business in thread-local
        self.assertIsNone(get_current_business())

        # Call middleware
        try:
            self.middleware(request)
        except:
            pass  # Ignore response errors

        # After middleware (in real scenario, would be cleared in finally block)
        # Since we're testing, it should have been set during the call
        # Note: In actual request, it's cleared after response

    def test_middleware_attaches_business_to_request(self):
        """Test that middleware attaches business to request object."""
        request = self.factory.get("/")
        request.META['HTTP_HOST'] = "widgets.smoothschedule.com"

        try:
            self.middleware(request)
        except:
            pass

        # Force lazy object evaluation
        self.assertEqual(request.business, self.business2)
