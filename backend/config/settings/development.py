"""Configuration de développement."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Celery en mode synchrone pour le dev (pas besoin de worker)
CELERY_TASK_ALWAYS_EAGER = True
