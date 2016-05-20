import os

BASE_DIR_local = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR_local), "static_dev", "static_root")
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR_local), "static_dev", "media_root")
