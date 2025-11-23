"""
Admin interface for resources app.
"""

from django.contrib import admin
from .models import Resource, Service


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "business", "user"]
    list_filter = ["type", "business"]
    search_fields = ["name"]
    readonly_fields = ["id"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "duration_minutes", "price", "business"]
    list_filter = ["business"]
    search_fields = ["name", "description"]
    readonly_fields = ["id"]
