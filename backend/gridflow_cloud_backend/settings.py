"""
Django settings for gridflow_cloud_backend project.

Uses django-environ for 12-factor configuration.
"""

import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
env = environ.Env(
    DJANGO_DEBUG=(bool, False),  # Default to False for security
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    ENVIRONMENT=(str, "development"),
)
environ.Env.read_env(BASE_DIR / ".env")

# Determine environment
ENVIRONMENT = env("ENVIRONMENT")
IS_PRODUCTION = ENVIRONMENT == "production"

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
# SECRET_KEY: In production, this MUST be set via environment variable
if IS_PRODUCTION:
    SECRET_KEY = env("DJANGO_SECRET_KEY")  # Will raise error if not set
else:
    SECRET_KEY = env(
        "DJANGO_SECRET_KEY",
        default="django-insecure-dev-only-change-in-production",
    )

DEBUG = env("DJANGO_DEBUG")

# In production, ensure ALLOWED_HOSTS is properly configured
if IS_PRODUCTION:
    ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")  # Must be set in production
else:
    ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_celery_beat",
    # Local
    "users",
    "organizations",
    "devices",
    "telemetry",
    "integrations",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gridflow_cloud_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gridflow_cloud_backend.wsgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL + TimescaleDB
# ---------------------------------------------------------------------------
if IS_PRODUCTION:
    # In production, DATABASE_URL must be explicitly set
    DATABASES = {
        "default": env.db("DATABASE_URL")
    }
else:
    # In development, fallback to SQLite for convenience
    DATABASES = {
        "default": env.db(
            "DATABASE_URL",
            default="sqlite:///db.sqlite3",
        )
    }

# ---------------------------------------------------------------------------
# Cache — Redis
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
    },
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
if IS_PRODUCTION:
    # In production, explicitly configure allowed origins
    CORS_ALLOWED_ORIGINS = env(
        "CORS_ALLOWED_ORIGINS",
        default="",
    ).split(",") if env("CORS_ALLOWED_ORIGINS", default="") else []
else:
    # Development-friendly settings
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Solar API Provider Defaults (platform-wide credentials)
# ---------------------------------------------------------------------------
# Note: In production, all API credentials should be set via environment variables
DEYE_BASE_URL = env("DEYE_BASE_URL", default="https://eu1-developer.deyecloud.com/v1.0")
DEYE_APP_ID = env("DEYE_APP_ID", default="")
DEYE_APP_SECRET = env("DEYE_APP_SECRET", default="")
DEYE_EMAIL = env("DEYE_EMAIL", default="")
DEYE_PASSWORD = env("DEYE_PASSWORD", default="")

SOLARMAN_BASE_URL = env("SOLARMAN_BASE_URL", default="https://api.solarmanpv.com")
SOLARMAN_APP_ID = env("SOLARMAN_APP_ID", default="")
SOLARMAN_APP_SECRET = env("SOLARMAN_APP_SECRET", default="")
SOLARMAN_EMAIL = env("SOLARMAN_EMAIL", default="")
SOLARMAN_PASSWORD = env("SOLARMAN_PASSWORD", default="")
SOLARMAN_PASSWORD_HASH = env("SOLARMAN_PASSWORD_HASH", default="")
SOLARMAN_LANGUAGE = env("SOLARMAN_LANGUAGE", default="en")

# ---------------------------------------------------------------------------
# Push Notifications (Firebase Cloud Messaging)
# ---------------------------------------------------------------------------
FCM_SERVER_KEY = env("FCM_SERVER_KEY", default="")

# ---------------------------------------------------------------------------
# Telemetry Configuration
# ---------------------------------------------------------------------------
# How often to poll provider APIs (in seconds). Default: 5 minutes.
TELEMETRY_SYNC_INTERVAL_SECONDS = int(env("TELEMETRY_SYNC_INTERVAL", default="300"))
# How many days of high-granularity data to retain. Default: 90 days.
TELEMETRY_RETENTION_DAYS = int(env("TELEMETRY_RETENTION_DAYS", default="90"))
