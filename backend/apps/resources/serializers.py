"""
Serializers for Resource and Service models.

MUST match TypeScript interfaces from api-schema.ts exactly.
"""

from rest_framework import serializers
from .models import Resource, Service


class ResourceSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Resource from api-schema.ts

    Fields:
    - id: string
    - name: string
    - type: ResourceType ('STAFF' | 'ROOM' | 'EQUIPMENT')
    - userId?: string
    """

    user_id = serializers.UUIDField(source="user.id", read_only=True, allow_null=True)

    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "type",
            "user_id",  # Maps to userId
        ]
        read_only_fields = ["id"]


class ServiceSerializer(serializers.ModelSerializer):
    """
    Matches TypeScript interface: Service from api-schema.ts

    Fields:
    - id: string
    - name: string
    - durationMinutes: number
    - price: number
    - description: string
    """

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "duration_minutes",  # Maps to durationMinutes
            "price",
            "description",
        ]
        read_only_fields = ["id"]
