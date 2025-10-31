from .base import *

DEBUG = True

INSTALLED_APPS += [
    # 'django_extensions',  # Потребує встановлення через requirements/development.txt
]

# Django Debug Toolbar (закоментовано, потребує встановлення через requirements/development.txt)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
#     INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
