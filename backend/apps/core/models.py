"""
Core models for multi-tenancy and user management.

Matches api-schema.ts TypeScript interfaces from the frontend.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import TenantManager, TenantManagerUnscoped


class Business(models.Model):
    """
    Tenant model - represents a business/organization using the platform.

    Matches TypeScript interface: Business from api-schema.ts

    Each business is isolated via subdomain (acme.smoothschedule.com) or
    custom domain (acmeauto.com). All other models have FK to Business.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("business name"), max_length=255)
    subdomain = models.SlugField(
        _("subdomain"),
        max_length=100,
        unique=True,
        help_text=_("URL subdomain (e.g., 'acme' for acme.smoothschedule.com)")
    )

    # Branding
    primary_color = models.CharField(_("primary color"), max_length=7, default="#3B82F6")
    secondary_color = models.CharField(_("secondary color"), max_length=7, default="#10B981")
    logo_url = models.URLField(_("logo URL"), blank=True, null=True)

    # White-labeling (paid tiers)
    whitelabel_enabled = models.BooleanField(
        _("white-label enabled"),
        default=False,
        help_text=_("Hide platform branding")
    )

    # Subscription (TODO: Implement in payments app)
    plan = models.CharField(
        _("subscription plan"),
        max_length=20,
        choices=[
            ("Free", "Free"),
            ("Professional", "Professional"),
            ("Business", "Business"),
            ("Enterprise", "Enterprise"),
        ],
        default="Free"
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Suspended", "Suspended"),
            ("Trial", "Trial"),
        ],
        default="Active"
    )
    joined_at = models.DateTimeField(_("joined at"), auto_now_add=True)

    # Policies (TODO: Implement policy enforcement logic)
    resources_can_reschedule = models.BooleanField(
        _("resources can reschedule"),
        default=False,
        help_text=_("Allow staff to reschedule their own appointments")
    )
    require_payment_method_to_book = models.BooleanField(
        _("require payment method"),
        default=False
    )
    cancellation_window_hours = models.IntegerField(
        _("cancellation window (hours)"),
        default=24
    )
    late_cancellation_fee_percent = models.IntegerField(
        _("late cancellation fee %"),
        default=0
    )

    # Website builder (TODO: Implement in separate app if needed)
    initial_setup_complete = models.BooleanField(_("setup complete"), default=False)
    active_template_id = models.CharField(_("active template"), max_length=100, blank=True)
    website_content = models.JSONField(_("website content"), default=dict, blank=True)
    website_pages = models.JSONField(_("website pages"), default=dict, blank=True)

    class Meta:
        verbose_name = _("business")
        verbose_name_plural = _("businesses")
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user model with multi-tenancy and role-based permissions.

    Matches TypeScript interface: User from api-schema.ts

    CRITICAL: Email is unique PER BUSINESS, not globally.
    Same email can exist for different businesses (maintains white-label isolation).
    """

    # UserRole from api-schema.ts
    ROLE_CHOICES = [
        ("superuser", "Superuser"),  # Platform admin
        ("platform_manager", "Platform Manager"),
        ("platform_support", "Platform Support"),
        ("owner", "Owner"),  # Business owner
        ("manager", "Manager"),  # Business manager
        ("staff", "Staff"),  # Staff member
        ("resource", "Resource"),  # Bookable resource (same as staff)
        ("customer", "Customer"),  # End customer
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,  # Platform users (superuser, platform_manager) have no business
        blank=True
    )
    role = models.CharField(_("role"), max_length=20, choices=ROLE_CHOICES)
    avatar_url = models.URLField(_("avatar URL"), blank=True, null=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        # CRITICAL: Email unique per business, not globally
        unique_together = [["email", "business"]]
        indexes = [
            models.Index(fields=["business", "email"]),
            models.Index(fields=["business", "role"]),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_role_display()})"

    # TODO: Implement permission checking methods
    # def has_permission(self, permission_name):
    #     """Check if user has specific permission based on role"""
    #     pass

    # def can_view_all_appointments(self):
    #     """Owner and Manager can view all appointments"""
    #     return self.role in ["owner", "manager"]


class TenantModel(models.Model):
    """
    Abstract base model for all multi-tenant models.

    Automatically adds business FK and ensures queries are scoped to business.
    All models that store business data should inherit from this.

    Managers:
        - objects: Automatically filters by current business (from thread-local)
        - objects_unscoped: Bypasses business filtering (use with caution!)

    Example:
        class Appointment(TenantModel):
            customer = models.ForeignKey(User, on_delete=models.CASCADE)
            # ...

        # In a view (with TenantMiddleware running):
        Appointment.objects.all()  # Only current business's appointments
        Appointment.objects_unscoped.all()  # All appointments (admin only!)
    """

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",  # Dynamic related name
        help_text=_("Business this record belongs to")
    )

    # Default manager: automatically scoped to current business
    objects = TenantManager()

    # Unscoped manager: for admin operations that need cross-business access
    objects_unscoped = TenantManagerUnscoped()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["business"]),
        ]
