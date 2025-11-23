"""
URL configuration for bookings app.

Implements endpoints from IMPLEMENTATION.md
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, BlockerViewSet

router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"blockers", BlockerViewSet, basename="blocker")

urlpatterns = [
    path("", include(router.urls)),
    # Availability endpoint at /api/v1/appointments/availability/
    # Registered via @action decorator in AppointmentViewSet
]

# TODO: Add booking endpoint (Phase 1)
# path("booking/", BookingView.as_view(), name="booking")
# - Public endpoint for customers to create appointment requests
# - Input: service, date/time, customer info
# - Output: Appointment object with status=PENDING
