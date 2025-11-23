"""
Custom managers for multi-tenant models.
"""

from django.db import models
from .threadlocals import get_current_business


class TenantManager(models.Manager):
    """
    Manager that automatically filters querysets by the current business.

    This manager is used by TenantModel to ensure all queries are scoped
    to the current business (tenant). The current business is stored in
    thread-local storage by TenantMiddleware.

    Usage:
        class MyModel(TenantModel):
            # Inherits objects = TenantManager()
            pass

        # Queries are automatically filtered by current business
        MyModel.objects.all()  # Only returns objects for current business

    For queries that need to bypass tenant filtering (e.g., admin operations),
    use the unscoped manager:
        MyModel.objects_unscoped.all()  # Returns all objects across all businesses
    """

    def get_queryset(self):
        """
        Override to automatically filter by current business.

        If no business is set in thread-local (e.g., background tasks, management
        commands), returns unfiltered queryset with a warning.
        """
        queryset = super().get_queryset()
        business = get_current_business()

        if business is not None:
            # Filter by current business
            return queryset.filter(business=business)
        else:
            # No business in thread-local - return unfiltered queryset
            # This happens in:
            # - Management commands
            # - Celery tasks
            # - Tests (unless explicitly set)
            # WARNING: Be careful with this - always set business explicitly in these contexts
            return queryset


class TenantManagerUnscoped(models.Manager):
    """
    Manager that bypasses tenant filtering.

    Use this for admin operations or when you explicitly need to query
    across all businesses. Always verify permissions before using this!

    Usage:
        MyModel.objects_unscoped.all()  # Returns all objects
    """

    def get_queryset(self):
        """Return unfiltered queryset (all businesses)."""
        return super().get_queryset()
