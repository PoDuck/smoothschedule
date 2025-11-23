"""
Serializers for core models.

MUST match TypeScript interfaces from api-schema.ts exactly.
"""

from rest_framework import serializers
from .models import Business, User


class BusinessSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Business from api-schema.ts

    Fields must match exactly:
    - id: string
    - name: string
    - subdomain: string
    - primaryColor: string (camelCase in JSON)
    - secondaryColor: string
    - logoUrl?: string
    - whitelabelEnabled: boolean
    - plan?: 'Free' | 'Professional' | 'Business' | 'Enterprise'
    - status?: 'Active' | 'Suspended' | 'Trial'
    - joinedAt?: Date
    - etc.
    """

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "subdomain",
            "primary_color",  # Maps to primaryColor in JSON
            "secondary_color",  # Maps to secondaryColor
            "logo_url",  # Maps to logoUrl
            "whitelabel_enabled",  # Maps to whitelabelEnabled
            "plan",
            "status",
            "joined_at",  # Maps to joinedAt
            # Policies
            "resources_can_reschedule",  # Maps to resourcesCanReschedule
            "require_payment_method_to_book",  # Maps to requirePaymentMethodToBook
            "cancellation_window_hours",  # Maps to cancellationWindowHours
            "late_cancellation_fee_percent",  # Maps to lateCancellationFeePercent
            # Website builder
            "initial_setup_complete",  # Maps to initialSetupComplete
            "active_template_id",  # Maps to activeTemplateId
            "website_content",  # Maps to websiteContent
            "website_pages",  # Maps to websitePages
        ]
        read_only_fields = ["id", "joined_at"]

    # TODO: Add field name transformation for camelCase
    # DRF returns snake_case by default, but frontend expects camelCase
    # Options:
    # 1. Use djangorestframework-camel-case package
    # 2. Override to_representation() to transform field names


class UserSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: User from api-schema.ts

    Fields:
    - id: string
    - name: string
    - email: string
    - role: UserRole
    - avatarUrl?: string
    - businessId?: string
    """

    business_id = serializers.UUIDField(source="business.id", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "name",  # TODO: Derived from first_name + last_name
            "email",
            "role",
            "avatar_url",  # Maps to avatarUrl
            "business_id",  # Maps to businessId
        ]
        read_only_fields = ["id"]

    def get_name(self, obj):
        """Return full name from Django User model"""
        return obj.get_full_name() or obj.email


# TODO: Implement camelCase field transformation
# from djangorestframework_camel_case.render import CamelCaseJSONRenderer
# Add to REST_FRAMEWORK settings in base.py:
# 'DEFAULT_RENDERER_CLASSES': ('djangorestframework_camel_case.render.CamelCaseJSONRenderer',)
