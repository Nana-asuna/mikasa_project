"""
Paramètres de sécurité avancés pour l'application orphelinat
"""
from .base import *
import os

# =============================================================================
# SÉCURITÉ GÉNÉRALE
# =============================================================================

# Clé secrète renforcée
SECRET_KEY = env('SECRET_KEY')
if not SECRET_KEY or len(str(SECRET_KEY)) < 50:
    raise ValueError("SECRET_KEY doit être définie et faire au moins 50 caractères")

# Debug désactivé en production
DEBUG = bool(env('DEBUG'))
if DEBUG and env('ENVIRONMENT') == 'production':
    raise ValueError("DEBUG ne peut pas être activé en production")

# Hosts autorisés
try:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
except Exception:
    ALLOWED_HOSTS = []

# =============================================================================
# SÉCURITÉ DES MOTS DE PASSE - PBKDF2 RENFORCÉ
# =============================================================================

# Utilisation de PBKDF2 avec SHA256 et plus d'itérations
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Par défaut
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Alternative moderne
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# Configuration PBKDF2 renforcée
PBKDF2_ITERATIONS = 600000  # Augmenté de 320000 à 600000

# Validation des mots de passe renforcée
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 14,  # Augmenté à 14 caractères minimum
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.accounts.validators.CustomPasswordValidator',
        'OPTIONS': {
            'min_uppercase': 2,
            'min_lowercase': 2,
            'min_digits': 2,
            'min_special': 2,
            'forbidden_patterns': ['123', 'abc', 'qwerty', 'password'],
        }
    },
]

# =============================================================================
# SÉCURITÉ HTTPS/TLS
# =============================================================================

# Force HTTPS en production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =============================================================================
# PROTECTION CSRF RENFORCÉE
# =============================================================================

# Protection CSRF
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
try:
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')
except Exception:
    CSRF_TRUSTED_ORIGINS = []
CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'

# Nom du cookie CSRF personnalisé
CSRF_COOKIE_NAME = 'orphanage_csrftoken'

# =============================================================================
# CONFIGURATION CORS SÉCURISÉE
# =============================================================================

# CORS - Configuration restrictive
try:
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
except Exception:
    CORS_ALLOWED_ORIGINS = []
try:
    CORS_ALLOWED_ORIGIN_REGEXES = env.list('CORS_ALLOWED_ORIGIN_REGEXES')
except Exception:
    CORS_ALLOWED_ORIGIN_REGEXES = []

CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400

# Méthodes HTTP autorisées
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Headers autorisés
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-api-version',
]

# =============================================================================
# EN-TÊTES DE SÉCURITÉ
# =============================================================================

# Protection XSS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Référer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# X-Frame-Options
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# CONTENT SECURITY POLICY (CSP)
# =============================================================================

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# =============================================================================
# PROTECTION CONTRE LES ATTAQUES PAR FORCE BRUTE
# =============================================================================

# Django Axes - Protection contre les attaques par force brute
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 heure
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'registration/locked_out.html'
AXES_VERBOSE = True

# =============================================================================
# SESSIONS SÉCURISÉES
# =============================================================================

# Configuration des sessions
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Nom du cookie de session personnalisé
SESSION_COOKIE_NAME = 'orphanage_sessionid'

# =============================================================================
# AUTHENTIFICATION À DEUX FACTEURS
# =============================================================================

# Configuration OTP
OTP_TOTP_ISSUER = 'Orphanage Management System'
OTP_LOGIN_URL = '/api/v1/auth/login/'
OTP_ADMIN_HIDE_SENSITIVE_DATA = True

# =============================================================================
# CHIFFREMENT DES DONNÉES SENSIBLES
# =============================================================================

# Clé de chiffrement pour les données sensibles
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY')
if not FIELD_ENCRYPTION_KEY:
    raise ValueError("FIELD_ENCRYPTION_KEY doit être définie")

# =============================================================================
# CONFORMITÉ RGPD
# =============================================================================

# Paramètres RGPD
GDPR_COMPLIANCE = {
    'DATA_RETENTION_DAYS': 2555,  # 7 ans pour les dossiers d'enfants
    'ANONYMIZATION_DELAY_DAYS': 30,  # Délai avant anonymisation
    'CONSENT_REQUIRED': True,
    'RIGHT_TO_BE_FORGOTTEN': True,
    'DATA_PORTABILITY': True,
    'BREACH_NOTIFICATION_HOURS': 72,
}

# =============================================================================
# AUDIT ET LOGGING SÉCURISÉ
# =============================================================================

# Configuration des logs sécurisés
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': 'SECURITY {levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'security',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# LIMITATION DE DÉBIT
# =============================================================================

# Configuration du rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Limites par défaut
DEFAULT_RATE_LIMITS = {
    'login': '5/m',
    'register': '3/m',
    'password_reset': '3/h',
    'api_general': '100/h',
    'api_sensitive': '20/h',
}

# =============================================================================
# VALIDATION DES FICHIERS UPLOADÉS
# =============================================================================

# Types de fichiers autorisés
ALLOWED_FILE_TYPES = {
    'images': ['image/jpeg', 'image/png', 'image/gif'],
    'documents': ['application/pdf', 'application/msword', 
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    'medical': ['application/pdf', 'image/jpeg', 'image/png'],
}

# Taille maximale des fichiers (en bytes)
MAX_FILE_SIZES = {
    'image': 5 * 1024 * 1024,  # 5MB
    'document': 10 * 1024 * 1024,  # 10MB
    'medical': 20 * 1024 * 1024,  # 20MB
}

# =============================================================================
# SÉCURITÉ DE LA BASE DE DONNÉES
# =============================================================================

# Configuration sécurisée de la base de données
DATABASES['default'].update({
    'OPTIONS': {
        'sslmode': 'require',
        'connect_timeout': 10,
        'options': '-c default_transaction_isolation=serializable'
    },
    'CONN_MAX_AGE': 60,
    'CONN_HEALTH_CHECKS': True,
})

# =============================================================================
# CACHE SÉCURISÉ
# =============================================================================

# Configuration du cache avec chiffrement
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'orphanage_secure',
        'TIMEOUT': 300,
        'VERSION': 1,
    }
}

# =============================================================================
# PERMISSIONS ET RÔLES
# =============================================================================

# Permissions par défaut strictes
DEFAULT_PERMISSION_CLASSES = [
    'rest_framework.permissions.IsAuthenticated',
    'apps.core.permissions.HasRequiredRole',
]

# Rôles et permissions
ROLE_PERMISSIONS = {
    'admin': ['*'],  # Toutes les permissions
    'soignant': ['view_child', 'add_medical_record', 'change_medical_record'],
    'assistant_social': ['view_child', 'add_child', 'change_child', 'view_family'],
    'logisticien': ['view_inventory', 'add_inventory', 'change_inventory'],
    'donateur': ['view_own_donations', 'add_donation'],
    'parrain': ['view_sponsored_children'],
    'visiteur': ['view_public_children'],
}
