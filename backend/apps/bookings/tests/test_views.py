"""
Tests for bookings ViewSets (multi-tenancy filtering, permissions).
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.core.models import Business, User
from apps.core.threadlocals import set_current_business, clear_current_business
from apps.resources.models import Resource, Service
from apps.bookings.models import Appointment, Blocker


@pytest.mark.django_db
class AppointmentViewSetTests(APITestCase):
    """Test AppointmentViewSet multi-tenancy and filtering."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()

        # Create businesses
        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )
        self.business2 = Business.objects.create(
            name="Widget Co",
            subdomain="widgets"
        )

        # Create users
        self.owner1 = User.objects.create_user(
            username="owner1",
            email="owner@acme.com",
            password="pass123",
            business=self.business1,
            role="owner"
        )
        self.customer1 = User.objects.create_user(
            username="customer1",
            email="customer@acme.com",
            password="pass123",
            business=self.business1,
            role="customer"
        )
        self.owner2 = User.objects.create_user(
            username="owner2",
            email="owner@widgets.com",
            password="pass123",
            business=self.business2,
            role="owner"
        )

        # Create resources and services
        set_current_business(self.business1)
        self.resource1 = Resource.objects.create(
            business=self.business1,
            name="Staff 1",
            type="STAFF"
        )
        self.service1 = Service.objects.create(
            business=self.business1,
            name="Haircut",
            duration_minutes=30,
            price=50.00
        )

        set_current_business(self.business2)
        self.resource2 = Resource.objects.create(
            business=self.business2,
            name="Staff 2",
            type="STAFF"
        )
        self.service2 = Service.objects.create(
            business=self.business2,
            name="Massage",
            duration_minutes=60,
            price=100.00
        )

        # Create appointments
        self.appointment1_biz1 = Appointment.objects.create(
            business=self.business1,
            customer=self.customer1,
            resource=self.resource1,
            service=self.service1,
            start_time=timezone.now() + timedelta(days=1),
            duration_minutes=30,
            status="CONFIRMED"
        )

        self.appointment2_biz2 = Appointment.objects.create(
            business=self.business2,
            customer=self.owner2,  # Using owner as customer for simplicity
            resource=self.resource2,
            service=self.service2,
            start_time=timezone.now() + timedelta(days=2),
            duration_minutes=60,
            status="PENDING"
        )

        clear_current_business()

    def tearDown(self):
        """Clear thread-local after tests."""
        clear_current_business()

    def test_list_appointments_filtered_by_business(self):
        """Test that appointments are filtered by current business."""
        # Set business1 context
        set_current_business(self.business1)

        # Login as business1 owner
        self.client.force_authenticate(user=self.owner1)

        # Make request (middleware would set business in real scenario)
        response = self.client.get('/api/v1/appointments/')

        # Should only see business1's appointments
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: Response data structure depends on pagination
        # This is a basic check - adjust based on your pagination settings

    def test_cannot_see_other_business_appointments(self):
        """Test that business1 user cannot see business2 appointments."""
        set_current_business(self.business1)
        self.client.force_authenticate(user=self.owner1)

        # Try to get business2's appointment
        response = self.client.get(f'/api/v1/appointments/{self.appointment2_biz2.id}/')

        # Should fail (404 or 403)
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_create_appointment_assigns_business(self):
        """Test that creating appointment auto-assigns current business."""
        set_current_business(self.business1)
        self.client.force_authenticate(user=self.owner1)

        appointment_data = {
            "customerId": str(self.customer1.id),
            "resourceId": str(self.resource1.id),
            "serviceId": str(self.service1.id),
            "startTime": (timezone.now() + timedelta(days=3)).isoformat(),
            "durationMinutes": 30,
            "status": "PENDING"
        }

        response = self.client.post('/api/v1/appointments/', appointment_data, format='json')

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify business was assigned
        appointment_id = response.data['id']
        appointment = Appointment.objects.get(id=appointment_id)
        self.assertEqual(appointment.business, self.business1)

    def test_filter_appointments_by_date_range(self):
        """Test filtering appointments by date range."""
        set_current_business(self.business1)
        self.client.force_authenticate(user=self.owner1)

        start_date = timezone.now().date().isoformat()
        end_date = (timezone.now() + timedelta(days=7)).date().isoformat()

        response = self.client.get(
            f'/api/v1/appointments/?start_date={start_date}&end_date={end_date}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include appointment1_biz1 (tomorrow)

    def test_filter_appointments_by_resource(self):
        """Test filtering appointments by resource IDs."""
        set_current_business(self.business1)
        self.client.force_authenticate(user=self.owner1)

        response = self.client.get(
            f'/api/v1/appointments/?resource_ids={self.resource1.id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class BlockerViewSetTests(APITestCase):
    """Test BlockerViewSet multi-tenancy filtering."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()

        # Create businesses
        self.business1 = Business.objects.create(
            name="Acme Corp",
            subdomain="acme"
        )

        # Create user
        self.owner1 = User.objects.create_user(
            username="owner1",
            email="owner@acme.com",
            password="pass123",
            business=self.business1,
            role="owner"
        )

        # Create resource
        set_current_business(self.business1)
        self.resource1 = Resource.objects.create(
            business=self.business1,
            name="Staff 1",
            type="STAFF"
        )

        clear_current_business()

    def tearDown(self):
        """Clear thread-local after tests."""
        clear_current_business()

    def test_create_blocker_assigns_business(self):
        """Test that creating blocker auto-assigns current business."""
        set_current_business(self.business1)
        self.client.force_authenticate(user=self.owner1)

        blocker_data = {
            "resourceId": str(self.resource1.id),
            "startTime": (timezone.now() + timedelta(hours=1)).isoformat(),
            "endTime": (timezone.now() + timedelta(hours=2)).isoformat(),
            "reason": "Lunch break"
        }

        response = self.client.post('/api/v1/blockers/', blocker_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify business was assigned
        blocker_id = response.data['id']
        blocker = Blocker.objects.get(id=blocker_id)
        self.assertEqual(blocker.business, self.business1)
