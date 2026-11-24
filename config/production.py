from .settings import *

DEBUG = False
DEBUG_TOOLBAR = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = [host.strip() for host in os.environ["DJANGO_ALLOWED_HOSTS"].split(",") if host.strip()]
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [item for item in MIDDLEWARE if not item.startswith("debug_toolbar.")]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
