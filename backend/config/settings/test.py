"""
Test settings - Use SQLite for testing instead of PostgreSQL.
"""

from .local import *  # noqa

# Allow all hosts in tests
ALLOWED_HOSTS = ["*"]

# Use SQLite for testing (no PostgreSQL required)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable debug toolbar in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
