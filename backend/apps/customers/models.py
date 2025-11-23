"""
Customer models.

Matches api-schema.ts TypeScript interfaces.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TenantModel, User


class Customer(TenantModel):
    """
    Customer profile (extended information beyond User model).

    Matches TypeScript interface: Customer from api-schema.ts

    API Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/customers/ - List customers
    - GET /api/v1/customers/{id}/ - Customer detail
    - PATCH /api/v1/customers/{id}/ - Update customer
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to User account (customer role)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        limit_choices_to={"role": "customer"},
        null=True,
        blank=True,
        help_text=_("User account if customer has login")
    )

    # Customer info
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20)

    # Address (optional)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=50, blank=True)
    zip = models.CharField(_("ZIP code"), max_length=10, blank=True)

    # Metrics
    total_spend = models.DecimalField(_("total spend"), max_digits=10, decimal_places=2, default=0)
    last_visit = models.DateTimeField(_("last visit"), null=True, blank=True)

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Inactive", "Inactive"),
            ("Blocked", "Blocked"),
        ],
        default="Active"
    )

    avatar_url = models.URLField(_("avatar URL"), blank=True, null=True)
    tags = models.JSONField(_("tags"), default=list, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "email"]),
            models.Index(fields=["business", "phone"]),
        ]

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    """
    Stored payment method (credit card).

    Matches TypeScript interface: PaymentMethod from api-schema.ts

    TODO: Integrate with Stripe (store stripe_payment_method_id)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="payment_methods"
    )

    # Payment method brand from api-schema.ts
    brand = models.CharField(
        _("brand"),
        max_length=20,
        choices=[
            ("Visa", "Visa"),
            ("Mastercard", "Mastercard"),
            ("Amex", "American Express"),
        ]
    )

    last4 = models.CharField(_("last 4 digits"), max_length=4)
    is_default = models.BooleanField(_("default payment method"), default=False)

    # Stripe integration
    stripe_payment_method_id = models.CharField(
        _("Stripe payment method ID"),
        max_length=255,
        blank=True,
        help_text=_("Stripe pm_xxx ID")
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.brand} ****{self.last4}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults
        if self.is_default:
            PaymentMethod.objects.filter(
                customer=self.customer,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
