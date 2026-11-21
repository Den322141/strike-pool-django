from .settings import *

DATABASES["default"]["NAME"] = BASE_DIR / "lab13.sqlite3"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
