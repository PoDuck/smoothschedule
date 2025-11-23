"""
Admin interface for bookings app.
"""

from django.contrib import admin
from .models import Appointment, Blocker


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["customer_name", "service", "resource", "start_time", "status", "business"]
    list_filter = ["status", "business", "resource"]
    search_fields = ["customer_name", "notes"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "start_time"


@admin.register(Blocker)
class BlockerAdmin(admin.ModelAdmin):
    list_display = ["title", "resource", "start_time", "duration_minutes", "business"]
    list_filter = ["business", "resource"]
    search_fields = ["title"]
    readonly_fields = ["id"]
    date_hierarchy = "start_time"
