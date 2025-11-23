"""
URL configuration for customers app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, PaymentMethodViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"payment-methods", PaymentMethodViewSet, basename="paymentmethod")

urlpatterns = [
    path("", include(router.urls)),
]
