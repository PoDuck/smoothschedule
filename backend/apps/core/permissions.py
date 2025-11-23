"""
Role-based permission classes for multi-tenant access control.

Implements granular permissions based on user roles:
- superuser, platform_manager, platform_support: Platform-level access
- owner: Full access to their business
- manager: Management access to their business
- staff/resource: Limited access to their own data
- customer: Read-only access to their own data
"""

from rest_framework import permissions


class IsOwnerOrManager(permissions.BasePermission):
    """
    Permission to only allow owners and managers to access.

    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsOwnerOrManager]
    """

    def has_permission(self, request, view):
        """Check if user is owner or manager."""
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in ["owner", "manager", "superuser", "platform_manager"]


class IsOwnerOnly(permissions.BasePermission):
    """
    Permission to only allow business owners.

    Use for sensitive operations like changing business settings, managing users, etc.
    """

    def has_permission(self, request, view):
        """Check if user is business owner or platform admin."""
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in ["owner", "superuser", "platform_manager"]


class IsStaffOrHigher(permissions.BasePermission):
    """
    Permission for staff members and above.

    Allows: owner, manager, staff, resource
    Denies: customer, unauthenticated
    """

    def has_permission(self, request, view):
        """Check if user is staff or higher role."""
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in [
            "owner",
            "manager",
            "staff",
            "resource",
            "superuser",
            "platform_manager",
            "platform_support",
        ]


class ReadOnly(permissions.BasePermission):
    """
    Permission that allows read-only access (GET, HEAD, OPTIONS).

    Denies all write operations (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        """Allow read-only methods."""
        return request.method in permissions.SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit.

    Anyone can read, but only the owner of an object can modify it.

    The object must have a `user` attribute or implement a `is_owner(user)` method.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns the object."""
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for object owner
        # Check if object has user attribute
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Check if object has is_owner method
        if hasattr(obj, "is_owner"):
            return obj.is_owner(request.user)

        # Default: deny if we can't determine ownership
        return False


class CustomerCanViewOwnData(permissions.BasePermission):
    """
    Customers can only view their own data.

    - Owners/Managers: View all data in their business
    - Customers: View only their own data

    Requires ViewSet to implement proper queryset filtering.
    """

    def has_permission(self, request, view):
        """All authenticated users have permission (filtering happens in queryset)."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if customer is viewing their own data."""
        # Owners and managers can view any object in their business
        if request.user.role in ["owner", "manager", "superuser", "platform_manager"]:
            return True

        # Customers can only view their own data
        if request.user.role == "customer":
            # Check if object has customer or user attribute
            if hasattr(obj, "customer"):
                return obj.customer == request.user
            if hasattr(obj, "user"):
                return obj.user == request.user

        # Staff/resources have limited access (implement separately if needed)
        return False


class StaffCanModifyOwnData(permissions.BasePermission):
    """
    Staff members can modify their own data.

    - Owners/Managers: Modify all data in their business
    - Staff/Resources: Modify only their own data
    - Customers: Read-only access to their own data

    Use for resources, blockers, etc.
    """

    def has_permission(self, request, view):
        """All authenticated users have permission."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check permissions based on user role."""
        # Owners and managers can modify anything in their business
        if request.user.role in ["owner", "manager", "superuser", "platform_manager"]:
            return True

        # Staff/resources can modify their own data
        if request.user.role in ["staff", "resource"]:
            # For write operations, check ownership
            if request.method not in permissions.SAFE_METHODS:
                if hasattr(obj, "resource"):
                    # Check if the resource is linked to this user
                    # (assuming Resource model has user FK)
                    return hasattr(obj.resource, "user") and obj.resource.user == request.user
                if hasattr(obj, "user"):
                    return obj.user == request.user

            # Staff can view anything in their business
            return request.method in permissions.SAFE_METHODS

        # Customers cannot modify
        return False


class PlatformAdminOnly(permissions.BasePermission):
    """
    Permission for platform administrators only.

    Use for platform-level operations that should not be accessible to business users.
    """

    def has_permission(self, request, view):
        """Check if user is platform admin."""
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in ["superuser", "platform_manager"]


# Composite permissions (combine multiple checks)


class OwnerOrManagerCanWrite(permissions.BasePermission):
    """
    Owner/Manager can write, others can only read.

    Common pattern for most business resources.
    """

    def has_permission(self, request, view):
        """Check permissions based on HTTP method."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Anyone authenticated can read
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only owner/manager can write
        return request.user.role in ["owner", "manager", "superuser", "platform_manager"]
