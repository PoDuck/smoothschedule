"""
WSGI config for SmoothSchedule.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
