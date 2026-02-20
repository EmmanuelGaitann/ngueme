"""
FIN.AI — Configuration Production

Usage:
    DJANGO_SETTINGS_MODULE=finai.settings.production python manage.py ...
    ou : from .production import *  dans __init__.py en prod
"""
from .base import *  # noqa
import os

# ── Sécurité ──────────────────────────────────────────────────────────────────
DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']  # Doit être défini en variable d'environnement

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# HTTPS — O2Switch termine SSL au niveau Apache (reverse proxy)
# Ce header indique à Django que la requête est bien HTTPS
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT            = True
SECURE_HSTS_SECONDS            = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_BROWSER_XSS_FILTER     = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'DENY'

# ── Base de données PostgreSQL (O2Switch / phpPgAdmin) ────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.environ['DB_NAME'],
        'USER':     os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST':     os.getenv('DB_HOST', 'localhost'),
        'PORT':     os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

# ── Fichiers statiques ────────────────────────────────────────────────────────
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Email (réinitialisation de mot de passe, alertes) ─────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@finai.cm')

# ── Logs ──────────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'finai.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ── Cache ─────────────────────────────────────────────────────────────────────
# Décommentez si Redis est disponible :
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#     }
# }
