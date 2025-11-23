"""
Multi-tenancy middleware for subdomain-based tenant resolution.

Extracts Business from subdomain (acme.smoothschedule.com) or custom domain (acmeauto.com).
Attaches business to request object for use in views/serializers.
"""

from django.conf import settings
from django.http import Http404
from django.utils.functional import SimpleLazyObject

from .models import Business


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
        # Not a tenant subdomain (could be platform subdomain or invalid)
        platform_subdomain = settings.PLATFORM_SUBDOMAIN
        if host.startswith(platform_subdomain):
            # Platform admin console - no business
            return None
        raise Http404("Invalid domain")

    # Extract subdomain from host
    subdomain = host.replace(domain_suffix, "")

    try:
        business = Business.objects.get(subdomain=subdomain)
        return business
    except Business.DoesNotExist:
        raise Http404(f"Business not found for subdomain: {subdomain}")


class TenantMiddleware:
    """
    Middleware that resolves current business from request and attaches to request.

    Usage in views:
        business = request.business

    TODO: Store business in thread-local for use in managers/querysets
    TODO: Add custom domain support (Phase 2)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use SimpleLazyObject to defer business lookup until accessed
        request.business = SimpleLazyObject(lambda: get_business_from_request(request))

        # TODO: Set thread-local for use in TenantManager
        # _thread_locals.business = request.business

        response = self.get_response(request)

        # TODO: Clear thread-local after request
        # _thread_locals.business = None

        return response


# TODO: Implement thread-local storage for business context
# import threading
# _thread_locals = threading.local()
#
# def get_current_business():
#     """Get current business from thread-local storage"""
#     return getattr(_thread_locals, 'business', None)
