"""
Booking models (appointments, blockers).

Matches api-schema.ts TypeScript interfaces.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TenantModel, User
from apps.resources.models import Resource, Service


class Appointment(TenantModel):
    """
    Customer appointment request/booking.

    Matches TypeScript interface: Appointment from api-schema.ts

    API Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/appointments/ - List appointments
      Filters: start_date, end_date, resource_ids
    - POST /api/v1/appointments/ - Create appointment
    - PATCH /api/v1/appointments/{id}/ - Update appointment (drag-and-drop)
    - GET /api/v1/booking/availability/ - Get available time slots
      Input: service_id, date, timezone
      Output: ["09:00", "09:30", ...] (server-side calculation)
    """

    # AppointmentStatus from api-schema.ts
    STATUS_CHOICES = [
        ("PENDING", "Pending Confirmation"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("NO_SHOW", "No Show"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Nullable resource (null = unassigned, shown in pending sidebar)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        help_text=_("Assigned resource (null if unassigned)")
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={"role": "customer"}
    )
    customer_name = models.CharField(
        _("customer name"),
        max_length=255,
        help_text=_("Denormalized for performance")
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments"
    )

    start_time = models.DateTimeField(_("start time"))
    duration_minutes = models.IntegerField(_("duration (minutes)"))

    status = models.CharField(_("status"), max_length=20, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(_("notes"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("appointment")
        verbose_name_plural = _("appointments")
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["business", "start_time"]),
            models.Index(fields=["business", "resource", "start_time"]),
            models.Index(fields=["business", "customer"]),
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.service.name} @ {self.start_time}"

    def save(self, *args, **kwargs):
        # Auto-populate customer_name from customer
        if not self.customer_name and self.customer:
            self.customer_name = self.customer.get_full_name() or self.customer.email
        super().save(*args, **kwargs)


class Blocker(TenantModel):
    """
    Time block (lunch break, vacation, maintenance window, etc.).

    Matches TypeScript interface: Blocker from api-schema.ts

    API Endpoints:
    - GET /api/v1/blockers/ - List blockers
    - POST /api/v1/blockers/ - Create blocker
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="blockers"
    )

    start_time = models.DateTimeField(_("start time"))
    duration_minutes = models.IntegerField(_("duration (minutes)"))
    title = models.CharField(_("title"), max_length=255)

    class Meta:
        verbose_name = _("blocker")
        verbose_name_plural = _("blockers")
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["business", "resource", "start_time"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.resource.name})"
