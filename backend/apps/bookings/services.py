"""
Business logic for availability calculation.

Calculates available time slots for booking appointments.
"""

from datetime import datetime, timedelta, time
from typing import List, Optional
from django.utils import timezone
from apps.core.models import Business, BusinessHours
from apps.resources.models import Resource, Service
from apps.bookings.models import Appointment, Blocker


def calculate_availability(
    business: Business,
    service: Service,
    date: datetime.date,
    resource_id: Optional[str] = None,
    timezone_name: str = "UTC"
) -> List[str]:
    """
    Calculate available time slots for a given service on a specific date.

    Args:
        business: Business instance
        service: Service to book
        date: Date to check availability
        resource_id: Optional specific resource ID
        timezone_name: Timezone for the date (e.g., "America/New_York")

    Returns:
        List of available time slots in HH:MM format (e.g., ["09:00", "09:30", "10:00"])

    Algorithm:
        1. Get business hours for the day of week
        2. Get all resources that can perform this service
        3. For each resource:
           - Get all appointments and blockers
           - Calculate free slots
        4. Return union of all available slots across resources
    """
    import pytz

    # Get timezone
    tz = pytz.timezone(timezone_name)

    # Get day of week (0=Monday, 6=Sunday)
    day_of_week = date.weekday()

    # Get business hours for this day
    business_hours = BusinessHours.objects.filter(
        business=business,
        day_of_week=day_of_week,
        is_closed=False
    ).order_by("open_time")

    if not business_hours.exists():
        # Business is closed on this day
        return []

    # Get resources
    if resource_id:
        resources = Resource.objects.filter(
            business=business,
            id=resource_id
        )
    else:
        # Get all resources that can perform this service
        # TODO: Add service-resource relationship
        resources = Resource.objects.filter(
            business=business,
            type__in=["STAFF", "ROOM"]  # Bookable resources
        )

    if not resources.exists():
        return []

    # Calculate slots for each resource and merge
    all_slots = set()

    for resource in resources:
        resource_slots = _calculate_resource_availability(
            business=business,
            resource=resource,
            service=service,
            date=date,
            business_hours=list(business_hours),
            tz=tz
        )
        all_slots.update(resource_slots)

    # Convert to sorted list
    return sorted(list(all_slots))


def _calculate_resource_availability(
    business: Business,
    resource: Resource,
    service: Service,
    date: datetime.date,
    business_hours: List[BusinessHours],
    tz
) -> List[str]:
    """
    Calculate availability for a specific resource.

    Args:
        business: Business instance
        resource: Resource to check
        service: Service being booked
        date: Date to check
        business_hours: List of BusinessHours for this day
        tz: Timezone

    Returns:
        List of available time slots in HH:MM format
    """
    # Service duration
    duration_minutes = service.duration_minutes
    slot_interval = 30  # 30-minute slots (could be configurable)

    # Get start and end of day in timezone
    day_start = datetime.combine(date, time.min).replace(tzinfo=tz)
    day_end = datetime.combine(date, time.max).replace(tzinfo=tz)

    # Get all appointments for this resource on this date
    appointments = Appointment.objects.filter(
        business=business,
        resource=resource,
        start_time__gte=day_start,
        start_time__lt=day_end,
        status__in=["PENDING", "CONFIRMED"]  # Exclude cancelled/no-show
    ).order_by("start_time")

    # Get all blockers for this resource on this date
    blockers = Blocker.objects.filter(
        business=business,
        resource=resource,
        start_time__lt=day_end,
        start_time__gte=day_start.replace(hour=0, minute=0, second=0)
    ).order_by("start_time")

    # Generate potential time slots from business hours
    potential_slots = []

    for hours in business_hours:
        # Convert business hours to datetime
        slot_start = datetime.combine(date, hours.open_time).replace(tzinfo=tz)
        slot_end = datetime.combine(date, hours.close_time).replace(tzinfo=tz)

        # Generate slots in intervals
        current_slot = slot_start
        while current_slot + timedelta(minutes=duration_minutes) <= slot_end:
            potential_slots.append(current_slot)
            current_slot += timedelta(minutes=slot_interval)

    # Filter out slots that conflict with appointments or blockers
    available_slots = []

    for slot in potential_slots:
        slot_end_time = slot + timedelta(minutes=duration_minutes)
        is_available = True

        # Check appointments
        for appointment in appointments:
            appt_end = appointment.start_time + timedelta(minutes=appointment.duration_minutes)
            # Check if slot overlaps with appointment
            if not (slot_end_time <= appointment.start_time or slot >= appt_end):
                is_available = False
                break

        if not is_available:
            continue

        # Check blockers
        for blocker in blockers:
            # Calculate blocker end time (blocker has duration_minutes, not end_time)
            blocker_end = blocker.start_time + timedelta(minutes=blocker.duration_minutes)
            # Check if slot overlaps with blocker
            if not (slot_end_time <= blocker.start_time or slot >= blocker_end):
                is_available = False
                break

        if is_available:
            # Format as HH:MM
            available_slots.append(slot.strftime("%H:%M"))

    return available_slots
