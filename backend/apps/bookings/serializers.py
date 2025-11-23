"""
Serializers for Appointment and Blocker models.

MUST match TypeScript interfaces from api-schema.ts exactly.
"""

from rest_framework import serializers
from .models import Appointment, Blocker


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Appointment from api-schema.ts

    Fields:
    - id: string
    - resourceId: string | null
    - customerId: string
    - customerName: string
    - serviceId: string
    - startTime: Date
    - durationMinutes: number
    - status: AppointmentStatus
    - notes?: string
    """

    resource_id = serializers.UUIDField(source="resource.id", allow_null=True, required=False)
    customer_id = serializers.UUIDField(source="customer.id")
    service_id = serializers.UUIDField(source="service.id")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "resource_id",  # Maps to resourceId
            "customer_id",  # Maps to customerId
            "customer_name",  # Maps to customerName
            "service_id",  # Maps to serviceId
            "start_time",  # Maps to startTime (Date)
            "duration_minutes",  # Maps to durationMinutes
            "status",
            "notes",
        ]
        read_only_fields = ["id", "customer_name"]

    # TODO: Implement create/update logic
    # - Validate resource belongs to same business
    # - Validate customer belongs to same business
    # - Validate service belongs to same business
    # - Auto-populate customer_name from customer
    # - Handle timezone conversion (store UTC, display local)


class BlockerSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Blocker from api-schema.ts

    Fields:
    - id: string
    - resourceId: string
    - startTime: Date
    - durationMinutes: number
    - title: string
    """

    resource_id = serializers.UUIDField(source="resource.id")

    class Meta:
        model = Blocker
        fields = [
            "id",
            "resource_id",  # Maps to resourceId
            "start_time",  # Maps to startTime
            "duration_minutes",  # Maps to durationMinutes
            "title",
        ]
        read_only_fields = ["id"]
