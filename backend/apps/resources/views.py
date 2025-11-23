"""
API views for Resource and Service models.

Implements endpoints from IMPLEMENTATION.md
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Resource, Service
from .serializers import ResourceSerializer, ServiceSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Resource model.

    Endpoints:
    - GET /api/v1/resources/ - List resources
    - POST /api/v1/resources/ - Create resource
    - PATCH /api/v1/resources/{id}/ - Update resource
    - DELETE /api/v1/resources/{id}/ - Delete resource

    TODO: Implement permissions
    - Owner/Manager can CRUD resources
    - Staff/Customers can view resources (read-only)
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Filter by request.business
    # def get_queryset(self):
    #     return Resource.objects.filter(business=self.request.business)

    # TODO: Auto-assign business on create
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Service model.

    Endpoints:
    - GET /api/v1/services/ - List services
    - POST /api/v1/services/ - Create service
    - PATCH /api/v1/services/{id}/ - Update service
    - DELETE /api/v1/services/{id}/ - Delete service

    TODO: Implement permissions
    - Owner/Manager can CRUD services
    - Staff/Customers can view services (read-only)
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Filter by request.business
    # def get_queryset(self):
    #     return Service.objects.filter(business=self.request.business)

    # TODO: Auto-assign business on create
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)
