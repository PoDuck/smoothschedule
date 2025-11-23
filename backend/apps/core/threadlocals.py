"""
Thread-local storage for multi-tenancy.

Stores the current business/tenant in thread-local storage so it can be
accessed by managers and models throughout the request lifecycle.
"""

import threading
from typing import Optional
from django.db.models import Model


_thread_locals = threading.local()


def set_current_business(business: Optional[Model]) -> None:
    """
    Set the current business for this thread.
    Called by TenantMiddleware for each request.

    Args:
        business: Business model instance or None
    """
    _thread_locals.business = business


def get_current_business() -> Optional[Model]:
    """
    Get the current business for this thread.
    Used by TenantManager to automatically filter queries.

    Returns:
        Business model instance or None
    """
    return getattr(_thread_locals, "business", None)


def clear_current_business() -> None:
    """
    Clear the current business from thread-local storage.
    Called at the end of each request.
    """
    if hasattr(_thread_locals, "business"):
        delattr(_thread_locals, "business")
