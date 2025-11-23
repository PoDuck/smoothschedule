"""
Serializers for Customer and PaymentMethod models.

MUST match TypeScript interfaces from api-schema.ts exactly.
"""

from rest_framework import serializers
from .models import Customer, PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: PaymentMethod from api-schema.ts

    Fields:
    - id: string
    - brand: 'Visa' | 'Mastercard' | 'Amex'
    - last4: string
    - isDefault: boolean
    """

    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "brand",
            "last4",
            "is_default",  # Maps to isDefault
        ]
        read_only_fields = ["id"]


class CustomerSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Customer from api-schema.ts

    Fields:
    - id: string
    - userId?: string
    - name: string
    - email: string
    - phone: string
    - city?: string
    - state?: string
    - zip?: string
    - totalSpend: number
    - lastVisit: Date | null
    - status: 'Active' | 'Inactive' | 'Blocked'
    - avatarUrl?: string
    - tags?: string[]
    - paymentMethods: PaymentMethod[]
    """

    user_id = serializers.UUIDField(source="user.id", read_only=True, allow_null=True)
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "user_id",  # Maps to userId
            "name",
            "email",
            "phone",
            "city",
            "state",
            "zip",
            "total_spend",  # Maps to totalSpend
            "last_visit",  # Maps to lastVisit
            "status",
            "avatar_url",  # Maps to avatarUrl
            "tags",
            "payment_methods",  # Maps to paymentMethods (nested)
        ]
        read_only_fields = ["id", "total_spend", "last_visit"]
