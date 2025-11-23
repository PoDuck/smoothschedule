"""
API views for Appointment and Blocker models.

Implements critical endpoints from IMPLEMENTATION.md
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import OwnerOrManagerCanWrite, StaffCanModifyOwnData
from .models import Appointment, Blocker
from .serializers import AppointmentSerializer, BlockerSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Appointment model.

    Critical Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/appointments/ - List appointments
      Filters: start_date, end_date, resource_ids
    - POST /api/v1/appointments/ - Create appointment
    - PATCH /api/v1/appointments/{id}/ - Update appointment (drag-and-drop)

    Multi-tenancy:
    - All queries automatically filtered by current business (via TenantManager)
    - Business automatically assigned on create
    """

    queryset = Appointment.objects.all()  # Auto-filtered by TenantManager
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, OwnerOrManagerCanWrite]

    def get_queryset(self):
        """
        Filter appointments by date range and resources.

        Query params:
        - start_date: ISO date string (YYYY-MM-DD)
        - end_date: ISO date string (YYYY-MM-DD)
        - resource_ids: Comma-separated list of resource IDs
        """
        # Base queryset is already filtered by business via TenantManager
        queryset = super().get_queryset()

        # Filter by date range (for scheduler view)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                start_time__gte=start_date,
                start_time__lte=end_date
            )

        # Filter by resources (for scheduler view)
        resource_ids = self.request.query_params.getlist('resource_ids')
        if resource_ids:
            queryset = queryset.filter(resource_id__in=resource_ids)

        return queryset

    def perform_create(self, serializer):
        """Auto-assign current business to new appointments."""
        serializer.save(business=self.request.business)

    @action(detail=False, methods=["get"], url_path="availability")
    def get_availability(self, request):
        """
        Get available time slots for booking.

        Query params:
        - service_id: UUID
        - date: YYYY-MM-DD
        - timezone: e.g., 'America/New_York'

        Returns:
        - List of available time slots: ["09:00", "09:30", "10:00", ...]

        TODO: Implement availability calculation logic
        - Get service duration
        - Get business hours for date
        - Get all appointments for date
        - Get all blockers for date
        - Calculate free slots considering:
          - Resource availability
          - Existing appointments
          - Blockers (lunch, breaks)
          - Buffer times
          - Business hours
        """
        # service_id = request.query_params.get('service_id')
        # date = request.query_params.get('date')
        # timezone = request.query_params.get('timezone')

        # TODO: Implement availability calculation
        return Response(
            {
                "error": "Availability calculation not yet implemented",
                "todo": "See IMPLEMENTATION.md for requirements"
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class BlockerViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Blocker model.

    Endpoints:
    - GET /api/v1/blockers/ - List blockers
    - POST /api/v1/blockers/ - Create blocker
    - PATCH /api/v1/blockers/{id}/ - Update blocker
    - DELETE /api/v1/blockers/{id}/ - Delete blocker

    Multi-tenancy:
    - All queries automatically filtered by current business (via TenantManager)
    - Business automatically assigned on create

    TODO: Implement role-based permissions
    - Owner/Manager can CRUD blockers
    - Staff can create blockers for themselves only
    """

    queryset = Blocker.objects.all()  # Auto-filtered by TenantManager
    serializer_class = BlockerSerializer
    permission_classes = [IsAuthenticated, StaffCanModifyOwnData]

    def perform_create(self, serializer):
        """Auto-assign current business to new blockers."""
        serializer.save(business=self.request.business)
