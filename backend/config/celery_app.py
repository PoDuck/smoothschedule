"""
Celery configuration for SmoothSchedule.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("smoothschedule")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    # Example: Check for upcoming appointments every 15 minutes
    "check-upcoming-appointments": {
        "task": "apps.bookings.tasks.check_upcoming_appointments",
        "schedule": crontab(minute="*/15"),
    },
    # Add more periodic tasks as needed
}
