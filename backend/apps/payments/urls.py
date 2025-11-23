"""
URL configuration for payments app.

TODO: Implement Stripe Connect integration (Phase 2)
"""

from django.urls import path

urlpatterns = [
    # TODO: Add Stripe Connect OAuth flow
    # path("connect/", StripeConnectView.as_view(), name="stripe-connect"),
    # path("connect/callback/", StripeConnectCallbackView.as_view(), name="stripe-callback"),

    # TODO: Add Stripe webhook endpoint
    # path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),

    # TODO: Add payment/refund endpoints
    # path("payments/", PaymentViewSet.as_view({'get': 'list'}), name="payments"),
    # path("refunds/", RefundView.as_view(), name="refunds"),
]
