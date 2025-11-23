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

    Multi-tenancy:
    - All queries automatically filtered by current business (via TenantManager)
    - Business automatically assigned on create

    TODO: Implement role-based permissions
    - Owner/Manager can CRUD customers
    - Staff can view customers (read-only)
    - Customers can view/update their own profile only
    """

    queryset = Customer.objects.all()  # Auto-filtered by TenantManager
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter customers based on user role.

        - Owner/Manager: See all customers in their business
        - Customer: See only their own profile
        """
        # Base queryset is already filtered by business via TenantManager
        queryset = super().get_queryset()

        # If customer role, only show their own profile
        if self.request.user.role == 'customer':
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """Auto-assign current business to new customers."""
        serializer.save(business=self.request.business)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    API endpoints for PaymentMethod model.

    Multi-tenancy:
    - Filtered by customer's business (via Customer foreign key)

    TODO: Integrate with Stripe
    - Create payment method via Stripe API
    - Store stripe_payment_method_id
    - Allow customers to manage their own payment methods
    """

    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter payment methods based on user role.

        - Customer: See only their own payment methods
        - Owner/Manager: See all payment methods in their business
        """
        # PaymentMethod doesn't inherit from TenantModel
        # It's related to Customer which is related to Business
        if self.request.user.role == 'customer':
            return PaymentMethod.objects.filter(
                customer__user=self.request.user
            )

        # For owner/manager, filter by business via customer relationship
        return PaymentMethod.objects.filter(
            customer__business=self.request.business
        )
