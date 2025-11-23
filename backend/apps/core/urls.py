"""
URL configuration for core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BusinessViewSet, UserViewSet

router = DefaultRouter()
router.register(r"businesses", BusinessViewSet, basename="business")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
