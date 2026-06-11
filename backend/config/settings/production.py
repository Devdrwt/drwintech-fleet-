"""Configuration de production — durcie (voir SECURITY.md)."""
from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env

DEBUG = False

# Origines de confiance CSRF (admin Django derrière HTTPS sur sous-domaine).
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# WhiteNoise : sert les fichiers statiques (collectstatic) sans serveur dédié.
# Inséré juste après le SecurityMiddleware (recommandation WhiteNoise).
MIDDLEWARE = (
    MIDDLEWARE[:1]
    + ["whitenoise.middleware.WhiteNoiseMiddleware"]
    + MIDDLEWARE[1:]
)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Sécurité transport
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
