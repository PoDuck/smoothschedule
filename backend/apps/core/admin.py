"""
Admin interface for core models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Business, User


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["name", "subdomain", "plan", "status", "joined_at"]
    list_filter = ["plan", "status"]
    search_fields = ["name", "subdomain"]
    readonly_fields = ["id", "joined_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "get_full_name", "role", "business", "is_active"]
    list_filter = ["role", "is_active", "business"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["id", "date_joined", "last_login"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "avatar_url")}),
        ("Business", {"fields": ("business", "role")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "business", "role"),
        }),
    )
