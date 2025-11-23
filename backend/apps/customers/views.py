"""
API views for Customer and PaymentMethod models.

Implements endpoints from IMPLEMENTATION.md
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Customer, PaymentMethod
from .serializers import CustomerSerializer, PaymentMethodSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Customer model.

    Endpoints (see IMPLEMENTATION.md):
    - GET /api/v1/customers/ - List customers
    - GET /api/v1/customers/{id}/ - Customer detail
    - POST /api/v1/customers/ - Create customer
    - PATCH /api/v1/customers/{id}/ - Update customer

    TODO: Implement permissions
    - Owner/Manager can CRUD customers
    - Staff can view customers (read-only)
    - Customers can view/update their own profile only
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Filter by request.business
    # def get_queryset(self):
    #     queryset = Customer.objects.filter(business=self.request.business)
    #
    #     # If customer role, only show their own profile
    #     if self.request.user.role == 'customer':
    #         queryset = queryset.filter(user=self.request.user)
    #
    #     return queryset

    # TODO: Auto-assign business on create
    # def perform_create(self, serializer):
    #     serializer.save(business=self.request.business)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    API endpoints for PaymentMethod model.

    TODO: Integrate with Stripe
    - Create payment method via Stripe API
    - Store stripe_payment_method_id
    - Allow customers to manage their own payment methods
    """

    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    # TODO: Filter by customer
    # def get_queryset(self):
    #     if self.request.user.role == 'customer':
    #         return PaymentMethod.objects.filter(
    #             customer__user=self.request.user
    #         )
    #     return PaymentMethod.objects.filter(
    #         customer__business=self.request.business
    #     )
