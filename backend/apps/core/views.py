"""
API views for core models (Business, User).

TODO: Implement tenant-scoped querysets (filter by request.business)
TODO: Implement permission checks (owner/manager/staff access control)
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Business, User
from .serializers import BusinessSerializer, UserSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Business model.

    List/Retrieve/Update business settings.

    TODO: Implement permissions
    - Only owner can update business settings
    - Staff can view business info (read-only)
    - Platform admins can view all businesses
    """

    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Override get_queryset() to filter by request.business
    # def get_queryset(self):
    #     if self.request.user.role in ['superuser', 'platform_manager']:
    #         return Business.objects.all()
    #     return Business.objects.filter(id=self.request.business.id)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for User model.

    List/Create/Update users within a business.

    TODO: Implement permissions
    - Owner/Manager can create/update users
    - Staff can view users in same business
    - Customers can only view/update their own profile
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Override get_queryset() to filter by request.business
    # def get_queryset(self):
    #     return User.objects.filter(business=self.request.business)

    # TODO: Override create() to auto-assign business
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)
