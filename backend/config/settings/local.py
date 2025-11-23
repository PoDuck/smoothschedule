"""
Local settings for development.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-local-development-key-change-in-production",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "*.smoothschedule.local"]

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# DJANGO DEBUG TOOLBAR
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# CORS - Allow all origins in development
# ------------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# Logging
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "apps": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
