"""
Admin interface for customers app.
"""

from django.contrib import admin
from .models import Customer, PaymentMethod


class PaymentMethodInline(admin.TabularInline):
    model = PaymentMethod
    extra = 0
    readonly_fields = ["id", "stripe_payment_method_id", "created_at"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "status", "total_spend", "last_visit", "business"]
    list_filter = ["status", "business"]
    search_fields = ["name", "email", "phone"]
    readonly_fields = ["id", "total_spend", "last_visit", "created_at", "updated_at"]
    inlines = [PaymentMethodInline]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["customer", "brand", "last4", "is_default", "created_at"]
    list_filter = ["brand", "is_default"]
    search_fields = ["customer__name", "last4"]
    readonly_fields = ["id", "stripe_payment_method_id", "created_at"]
