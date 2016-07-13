import os

BASE_DIR_local = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR_local), "static_dev", "static_root")
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR_local), "static_dev", "media_root")

# Django Rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'custom_package.api_negotiation.IgnoreClientContentNegotiation',
    'PAGE_SIZE': 10
}

# Recaptcha SSL
RECAPTCHA_USE_SSL = False
