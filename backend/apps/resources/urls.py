"""
URL configuration for resources app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ResourceViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r"resources", ResourceViewSet, basename="resource")
router.register(r"services", ServiceViewSet, basename="service")

urlpatterns = [
    path("", include(router.urls)),
]
