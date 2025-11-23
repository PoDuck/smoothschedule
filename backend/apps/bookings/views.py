"""
API views for Appointment and Blocker models.

Implements critical endpoints from IMPLEMENTATION.md
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    TODO: Implement scheduler-specific endpoints
    - GET /api/v1/booking/availability/ - Available time slots
      Input: service_id, date, timezone
      Output: ["09:00", "09:30", ...]
      Logic: Server-side calculation considering Resources, Blockers, Business Hours
    """

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Implement filtering by date range and resources
    # def get_queryset(self):
    #     queryset = Appointment.objects.filter(business=self.request.business)
    #
    #     # Filter by date range (for scheduler view)
    #     start_date = self.request.query_params.get('start_date')
    #     end_date = self.request.query_params.get('end_date')
    #     if start_date and end_date:
    #         queryset = queryset.filter(
    #             start_time__gte=start_date,
    #             start_time__lte=end_date
    #         )
    #
    #     # Filter by resources (for scheduler view)
    #     resource_ids = self.request.query_params.getlist('resource_ids')
    #     if resource_ids:
    #         queryset = queryset.filter(resource_id__in=resource_ids)
    #
    #     return queryset

    # TODO: Auto-assign business on create
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)

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

    TODO: Implement permissions
    - Owner/Manager can CRUD blockers
    - Staff can create blockers for themselves
    """

    queryset = Blocker.objects.all()
    serializer_class = BlockerSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Filter by request.business
    # def get_queryset(self):
    #     return Blocker.objects.filter(business=self.request.business)

    # TODO: Auto-assign business on create
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)
