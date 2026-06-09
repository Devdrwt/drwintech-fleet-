"""
Configuration de base — Drwintech Fleet.
Partagée par development.py et production.py.
"""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# --- Applications ---
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "channels",
]

# Contextes délimités (monolithe modulaire — voir ADR 0005)
LOCAL_APPS = [
    "apps.accounts",
    "apps.crm",
    "apps.fleet",
    "apps.telemetry",
    "apps.geofencing",
    "apps.billing",
    "apps.maintenance",
    "apps.notifications",
    "apps.reporting",
    "apps.audit",
    "apps.integrations",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.audit.middleware.AuditLogMiddleware",  # audit append-only (voir SECURITY.md)
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Bases de données : métier (default) + télémétrie (timescale) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="fleet"),
        "USER": env("DB_USER", default="fleet"),
        "PASSWORD": env("DB_PASSWORD", default="fleet"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    },
    "telemetry": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("TSDB_NAME", default="fleet_telemetry"),
        "USER": env("TSDB_USER", default="fleet"),
        "PASSWORD": env("TSDB_PASSWORD", default="fleet"),
        "HOST": env("TSDB_HOST", default="localhost"),
        "PORT": env("TSDB_PORT", default="5433"),
    },
}
DATABASE_ROUTERS = ["config.db_routers.TelemetryRouter"]

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]
# Argon2 en tête (voir SECURITY.md)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "config.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("ACCESS_TOKEN_LIFETIME_MIN", default=30)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("REFRESH_TOKEN_LIFETIME_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Drwintech Fleet API",
    "DESCRIPTION": "Plateforme indépendante de gestion de flotte GPS.",
    "VERSION": "1.0.0",
}

# --- Celery ---
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = "json"

# --- Channels (temps réel) ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [env("REDIS_URL", default="redis://localhost:6379/0")]},
    },
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)
CORS_ALLOW_CREDENTIALS = True

# --- Traccar (moteur d'ingestion) ---
TRACCAR_API_URL = env("TRACCAR_API_URL", default="http://localhost:8082/api")
TRACCAR_WS_URL = env("TRACCAR_WS_URL", default="ws://localhost:8082/api/socket")
TRACCAR_SERVICE_USER = env("TRACCAR_SERVICE_USER", default="")
TRACCAR_SERVICE_PASSWORD = env("TRACCAR_SERVICE_PASSWORD", default="")

# --- Web Push (VAPID) ---
VAPID_PUBLIC_KEY = env("VAPID_PUBLIC_KEY", default="")
VAPID_PRIVATE_KEY_PATH = env(
    "VAPID_PRIVATE_KEY_PATH", default=str(BASE_DIR / "infra" / "vapid_private.pem")
)
VAPID_CONTACT_EMAIL = env("VAPID_CONTACT_EMAIL", default="admin@drwintech.com")

# --- Métier ---
DEFAULT_CURRENCY = env("DEFAULT_CURRENCY", default="XOF")
PAYMENT_GRACE_DAYS = env.int("PAYMENT_GRACE_DAYS", default=7)
SIM_LOW_BALANCE_THRESHOLD_PERCENT = env.int(
    "SIM_LOW_BALANCE_THRESHOLD_PERCENT", default=20
)

# --- I18N ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
