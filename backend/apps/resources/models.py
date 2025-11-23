"""
Resource models (staff, rooms, equipment, etc.).

Matches api-schema.ts TypeScript interfaces.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TenantModel, User


class Resource(TenantModel):
    """
    Bookable resource (staff member, room, equipment, vehicle, etc.).

    Matches TypeScript interface: Resource from api-schema.ts

    API Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/resources/ - List resources
    - POST /api/v1/resources/ - Create resource
    - PATCH /api/v1/resources/{id}/ - Update resource
    - DELETE /api/v1/resources/{id}/ - Delete resource
    """

    # ResourceType from api-schema.ts
    TYPE_CHOICES = [
        ("STAFF", "Staff Member"),
        ("ROOM", "Room/Bay"),
        ("EQUIPMENT", "Equipment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255, help_text=_("e.g., 'Bay 1', 'John (Mechanic)'"))
    type = models.CharField(_("type"), max_length=20, choices=TYPE_CHOICES)

    # Link to User if this resource is a person (staff member)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
        help_text=_("User account if this resource is a staff member")
    )

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["business", "type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Service(TenantModel):
    """
    Service offered by business (Oil Change, Haircut, etc.).

    Matches TypeScript interface: Service from api-schema.ts

    API Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/services/ - List services
    - POST /api/v1/services/ - Create service
    - PATCH /api/v1/services/{id}/ - Update service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255)
    duration_minutes = models.IntegerField(_("duration (minutes)"))
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    description = models.TextField(_("description"))

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")
        ordering = ["name"]

    def __str__(self):
        return self.name
