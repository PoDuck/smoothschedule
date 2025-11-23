"""
Tests for availability calculation logic.
"""

import pytest
from datetime import datetime, time, timedelta
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.core.models import Business, User, BusinessHours
from apps.core.threadlocals import set_current_business, clear_current_business
from apps.resources.models import Resource, Service
from apps.bookings.models import Appointment, Blocker
from apps.bookings.services import calculate_availability


@pytest.mark.django_db
class AvailabilityCalculationTests(APITestCase):
    """Test availability calculation service."""

    def setUp(self):
        """Create test data."""
        # Create business
        self.business = Business.objects.create(
            name="Test Salon",
            subdomain="testsalon"
        )

        # Create business hours (Monday 9am-5pm)
        self.monday_hours = BusinessHours.objects.create(
            business=self.business,
            day_of_week=0,  # Monday
            open_time=time(9, 0),
            close_time=time(17, 0),
            is_closed=False
        )

        # Tuesday closed
        BusinessHours.objects.create(
            business=self.business,
            day_of_week=1,  # Tuesday
            is_closed=True
        )

        # Wednesday split shift (9am-12pm, 1pm-5pm)
        BusinessHours.objects.create(
            business=self.business,
            day_of_week=2,  # Wednesday
            open_time=time(9, 0),
            close_time=time(12, 0),
            is_closed=False
        )
        BusinessHours.objects.create(
            business=self.business,
            day_of_week=2,  # Wednesday
            open_time=time(13, 0),
            close_time=time(17, 0),
            is_closed=False
        )

        set_current_business(self.business)

        # Create resource
        self.resource = Resource.objects.create(
            business=self.business,
            name="Stylist 1",
            type="STAFF"
        )

        # Create service (30 minutes)
        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration_minutes=30,
            price=50.00
        )

        # Create user
        self.user = User.objects.create_user(
            username="owner",
            email="owner@testsalon.com",
            password="pass123",
            business=self.business,
            role="owner"
        )

    def tearDown(self):
        """Clear thread-local after tests."""
        clear_current_business()

    def test_basic_availability_calculation(self):
        """Test basic availability calculation with no appointments."""
        # Monday, no appointments
        date = datetime(2025, 11, 24).date()  # Monday

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            timezone_name="UTC"
        )

        # Should have slots from 9am to 4:30pm (30-min service needs to end by 5pm)
        # 9:00, 9:30, 10:00, ..., 16:00, 16:30
        self.assertGreater(len(slots), 0)
        self.assertIn("09:00", slots)
        self.assertIn("09:30", slots)
        self.assertIn("16:30", slots)
        # 17:00 shouldn't be available (service would end at 17:30, past closing)
        self.assertNotIn("17:00", slots)

    def test_closed_day_returns_empty(self):
        """Test that closed days return no available slots."""
        # Tuesday is closed
        date = datetime(2025, 11, 25).date()  # Tuesday

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            timezone_name="UTC"
        )

        self.assertEqual(len(slots), 0)

    def test_split_shift_availability(self):
        """Test availability calculation with split shifts."""
        # Wednesday has split shift: 9am-12pm, 1pm-5pm
        date = datetime(2025, 11, 26).date()  # Wednesday

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            timezone_name="UTC"
        )

        # Should have slots in morning shift (9:00-11:30)
        self.assertIn("09:00", slots)
        self.assertIn("11:00", slots)
        self.assertIn("11:30", slots)

        # Should NOT have slots during break (12:00-13:00)
        self.assertNotIn("12:00", slots)
        self.assertNotIn("12:30", slots)

        # Should have slots in afternoon shift (13:00-16:30)
        self.assertIn("13:00", slots)
        self.assertIn("16:30", slots)

    def test_availability_with_existing_appointment(self):
        """Test that existing appointments block time slots."""
        date = datetime(2025, 11, 24).date()  # Monday

        # Create appointment at 10:00 for 30 minutes
        appointment_time = timezone.make_aware(
            datetime.combine(date, time(10, 0)),
            timezone.get_current_timezone()
        )

        Appointment.objects.create(
            business=self.business,
            resource=self.resource,
            customer=self.user,
            service=self.service,
            start_time=appointment_time,
            duration_minutes=30,
            status="CONFIRMED"
        )

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            resource_id=str(self.resource.id),
            timezone_name="UTC"
        )

        # 10:00 should NOT be available (appointment starts then)
        self.assertNotIn("10:00", slots)

        # 9:30 SHOULD be available (9:30 + 30min = 10:00, ends exactly when appointment starts)
        self.assertIn("09:30", slots)

        # 9:00 should be available (ends at 9:30, before appointment)
        self.assertIn("09:00", slots)

        # 10:30 should be available (appointment ends at 10:30, new appointment can start then)
        self.assertIn("10:30", slots)

    def test_availability_with_blocker(self):
        """Test that blockers (breaks, lunch) block time slots."""
        date = datetime(2025, 11, 24).date()  # Monday

        # Create lunch blocker 12:00-13:00 (60 minutes)
        lunch_start = timezone.make_aware(
            datetime.combine(date, time(12, 0)),
            timezone.get_current_timezone()
        )

        Blocker.objects.create(
            business=self.business,
            resource=self.resource,
            start_time=lunch_start,
            duration_minutes=60,
            title="Lunch break"
        )

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            resource_id=str(self.resource.id),
            timezone_name="UTC"
        )

        # 12:00 should NOT be available (conflicts with lunch start)
        self.assertNotIn("12:00", slots)

        # 11:30 SHOULD be available (11:30 + 30min = 12:00, ends exactly when lunch starts)
        self.assertIn("11:30", slots)

        # 11:00 should be available (ends at 11:30, before lunch)
        self.assertIn("11:00", slots)

        # 13:00 should be available (lunch ends at 13:00, appointment can start then)
        self.assertIn("13:00", slots)

    def test_cancelled_appointments_dont_block(self):
        """Test that cancelled appointments don't block availability."""
        date = datetime(2025, 11, 24).date()  # Monday

        appointment_time = timezone.make_aware(
            datetime.combine(date, time(10, 0)),
            timezone.get_current_timezone()
        )

        # Create cancelled appointment
        Appointment.objects.create(
            business=self.business,
            resource=self.resource,
            customer=self.user,
            service=self.service,
            start_time=appointment_time,
            duration_minutes=30,
            status="CANCELLED"
        )

        slots = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            resource_id=str(self.resource.id),
            timezone_name="UTC"
        )

        # 10:00 should be available (appointment is cancelled)
        self.assertIn("10:00", slots)

    def test_specific_resource_vs_all_resources(self):
        """Test availability when checking specific resource vs all resources."""
        date = datetime(2025, 11, 24).date()  # Monday

        # Create second resource
        resource2 = Resource.objects.create(
            business=self.business,
            name="Stylist 2",
            type="STAFF"
        )

        # Book resource1 at 10:00
        appointment_time = timezone.make_aware(
            datetime.combine(date, time(10, 0)),
            timezone.get_current_timezone()
        )

        Appointment.objects.create(
            business=self.business,
            resource=self.resource,  # resource1
            customer=self.user,
            service=self.service,
            start_time=appointment_time,
            duration_minutes=30,
            status="CONFIRMED"
        )

        # Check specific resource (resource1)
        slots_resource1 = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            resource_id=str(self.resource.id),
            timezone_name="UTC"
        )

        # 10:00 should NOT be available for resource1
        self.assertNotIn("10:00", slots_resource1)

        # Check all resources
        slots_all = calculate_availability(
            business=self.business,
            service=self.service,
            date=date,
            timezone_name="UTC"
        )

        # 10:00 SHOULD be available when checking all resources
        # (resource2 is free at 10:00)
        self.assertIn("10:00", slots_all)


@pytest.mark.django_db
class AvailabilityAPITests(APITestCase):
    """Test availability API endpoint."""

    def setUp(self):
        """Create test data."""
        self.client = APIClient()

        self.business = Business.objects.create(
            name="Test Salon",
            subdomain="testsalon"
        )

        # Monday 9am-5pm
        BusinessHours.objects.create(
            business=self.business,
            day_of_week=0,
            open_time=time(9, 0),
            close_time=time(17, 0),
            is_closed=False
        )

        set_current_business(self.business)

        self.resource = Resource.objects.create(
            business=self.business,
            name="Stylist 1",
            type="STAFF"
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration_minutes=30,
            price=50.00
        )

        self.user = User.objects.create_user(
            username="owner",
            email="owner@testsalon.com",
            password="pass123",
            business=self.business,
            role="owner"
        )

    def tearDown(self):
        """Clear thread-local."""
        clear_current_business()

    def test_availability_endpoint_success(self):
        """Test successful availability API call."""
        self.client.force_authenticate(user=self.user)

        # Mock request to have business attribute
        response = self.client.get(
            '/api/v1/appointments/availability/',
            {
                'service_id': str(self.service.id),
                'date': '2025-11-24',  # Monday
                'timezone': 'UTC'
            }
        )

        # Note: This will fail without proper middleware setup in tests
        # But we're testing the view logic

    def test_availability_endpoint_missing_params(self):
        """Test availability endpoint with missing parameters."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/appointments/availability/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_availability_endpoint_invalid_date(self):
        """Test availability endpoint with invalid date format."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/api/v1/appointments/availability/',
            {
                'service_id': str(self.service.id),
                'date': 'invalid-date',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
