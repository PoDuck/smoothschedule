"""
Multi-tenancy middleware for subdomain-based tenant resolution.

Extracts Business from subdomain (acme.smoothschedule.com) or custom domain (acmeauto.com).
Attaches business to request object for use in views/serializers.
Stores business in thread-local storage for automatic query filtering via TenantManager.
"""

from django.conf import settings
from django.http import Http404
from django.utils.functional import SimpleLazyObject

from .models import Business
from .threadlocals import set_current_business, clear_current_business


def get_business_from_request(request):
    """
    Extract business from request host.

    Priority:
    1. Custom domain (e.g., acmeauto.com)
    2. Subdomain (e.g., acme.smoothschedule.com)

    Returns:
        Business instance or raises Http404
    """
    host = request.get_host().split(":")[0]  # Remove port if present

    # TODO: Check custom domain first (Phase 2 feature)
    # try:
    #     business = Business.objects.get(
    #         custom_domain=host,
    #         custom_domain_verified=True
    #     )
    #     return business
    # except Business.DoesNotExist:
    #     pass

    # Extract subdomain
    domain_suffix = settings.TENANT_DOMAIN_SUFFIX  # e.g., ".smoothschedule.com"

    if not host.endswith(domain_suffix):
        # Not using platform domain - invalid request
        raise Http404("Invalid domain")

    # Extract subdomain from host
    subdomain = host.replace(domain_suffix, "")

    # Check if this is the platform subdomain
    platform_subdomain = settings.PLATFORM_SUBDOMAIN
    if subdomain == platform_subdomain:
        # Platform admin console - no business
        return None

    # Look up business by subdomain
    try:
        business = Business.objects.get(subdomain=subdomain)
        return business
    except Business.DoesNotExist:
        raise Http404(f"Business not found for subdomain: {subdomain}")


class TenantMiddleware:
    """
    Middleware that resolves current business from request and attaches to request.

    This middleware:
    1. Extracts business from subdomain/domain
    2. Attaches business to request object (request.business)
    3. Stores business in thread-local storage for TenantManager to use
    4. Clears thread-local after request completes

    Usage in views:
        business = request.business

    TODO: Add custom domain support (Phase 2)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use SimpleLazyObject to defer business lookup until accessed
        request.business = SimpleLazyObject(lambda: get_business_from_request(request))

        try:
            # Force evaluation of lazy object and store in thread-local
            # This makes the business available to TenantManager for automatic filtering
            business = request.business
            set_current_business(business)

            response = self.get_response(request)

            return response
        finally:
            # Always clear thread-local after request (even if exception occurs)
            # This prevents business from leaking between requests in same thread
            clear_current_business()
