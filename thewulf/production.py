from .common import *


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(USERHOME, 'tmp/django_cache'),  # -> /home/mwinter80/tmp/django_cache
    }
}

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 6000
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get("EMAILPASS", "")
EMAIL_HOST_USER = 'info@thewulf.org'
EMAIL_Port = 587
EMAIL_USE_TLS = True
