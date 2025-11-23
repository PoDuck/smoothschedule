"""
Custom authentication backends for multi-tenant authentication.

Since email is unique per business (not globally), we need custom authentication
that takes both email and business into account.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import Business

User = get_user_model()


class BusinessScopedAuthBackend(ModelBackend):
    """
    Authentication backend that scopes users by business.

    This backend is necessary because email is unique per business, not globally.
    The same email can exist for different businesses (maintaining white-label isolation).

    Usage:
        1. Frontend sends email + password to login
        2. Business is determined from subdomain (via TenantMiddleware)
        3. This backend authenticates user by email + business combination

    Example:
        # john@example.com can exist in multiple businesses:
        - Business A (subdomain: acme) has john@example.com
        - Business B (subdomain: widgets) has john@example.com

        When logging in at acme.smoothschedule.com with john@example.com:
        - TenantMiddleware resolves Business A from subdomain
        - This backend authenticates john@example.com in Business A

    Configuration:
        Add to settings.py:
        AUTHENTICATION_BACKENDS = [
            'apps.core.auth.BusinessScopedAuthBackend',
            'django.contrib.auth.backends.ModelBackend',  # Fallback
        ]
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by email + business + password.

        Args:
            request: HTTP request (contains request.business from TenantMiddleware)
            username: User's email address
            password: User's password
            **kwargs: Additional arguments

        Returns:
            User instance if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None

        # Get business from request (set by TenantMiddleware)
        business = getattr(request, 'business', None)

        if business is None:
            # No business in request - possibly platform login
            # Fall back to email-only authentication for platform users
            try:
                user = User.objects.get(
                    email=username,
                    business__isnull=True  # Platform users have no business
                )
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return None
        else:
            # Business-scoped authentication
            try:
                user = User.objects.get(
                    email=username,
                    business=business
                )
            except User.DoesNotExist:
                # User not found in this business
                return None

        # Check password
        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by ID (standard Django method).

        Args:
            user_id: User's primary key (UUID)

        Returns:
            User instance or None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
