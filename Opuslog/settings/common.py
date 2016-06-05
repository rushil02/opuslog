"""
Django settings for Opuslog project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

import psycopg2


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^@j4m-ff2wcago%qkos@4$q(8#0jm6rkp#k3#hcq#9xdy2a9lr'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',

    'cities_light',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.facebook', # FIXME: uncomment when ready
    # 'allauth.socialaccount.providers.google',  # FIXME: uncomment when ready, *tested - working*
    'debug_toolbar',
    'tinymce',
    'rest_framework',
    'djcelery',

    'user_custom',
    'publication',
    'write_up',
    'engagement',
    'essential',
    'log',
    'admin_custom',
    'staff_custom',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Opuslog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Opuslog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'OpuslogDB',
        'USER': 'MooPoint',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,  # TODO: change if needed
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'


# Django all-auth
# http://django-allauth.readthedocs.io/en/latest/configuration.html
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_ADAPTER = 'admin_custom.all_auth_adapter.CustomAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username'  # Login field
ACCOUNT_CONFIRM_EMAIL_ON_GET = False  # User has to click a button on the redirected page
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_REDIRECT_URL  # Redirect to '/'
ACCOUNT_EMAIL_REQUIRED = True  # Email required for signing up
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Opuslog.com - "
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 3600  # User is blocked for this time after failure to repeatedly log in
# Social Account Providers setup  Docs - http://django-allauth.readthedocs.io/en/stable/providers.html
SOCIALACCOUNT_PROVIDERS = \
    {'facebook':
         {'METHOD': 'oauth2',
          'SCOPE': ['email', 'public_profile'],
          'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
          'FIELDS': [
              'id',
              'email',
              'name',
              'first_name',
              'last_name',
              'verified',
              'locale',
              'timezone',
              'link',
              'gender',
              'updated_time'],
          'VERIFIED_EMAIL': False,
          'VERSION': 'v2.4'},
     'google':
         {'SCOPE': ['profile', 'email'],
          'AUTH_PARAMS': {'access_type': 'online'}}
     }


# used by django.contrib.site
SITE_ID = 1


# Cities-light settings
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en', ]
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IN', ]


# Email settings
EMAIL_HOST_USER = 'moopoint1402@gmail.com'
EMAIL_HOST_PASSWORD = 'sappy8086'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Domain name settings
WEBSITE_DOMAIN = 'www.opuslog.com'


# django-tinymce
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True


# Extended Auth user model
AUTH_USER_MODEL = 'user_custom.User'


# Celery settings
# http://celery.readthedocs.org/en/latest/index.html
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
BROKER_HEARTBEAT = 10
BROKER_HEARTBEAT_CHECKRATE = 2
# BROKER_POOL_LIMIT = 10  # default
BROKER_URL = 'amqp://MooPoint:s@ppy8086@localhost:5672/MooPointHost'
CELERY_TASK_RESULT_EXPIRES = 0
CELERY_TRACK_STARTED = True
# CELERYD_TASK_TIME_LIMIT = 180
CELERY_SEND_EVENTS = True
CELERY_SEND_TASK_SENT_EVENT = True
CELERY_DISABLE_RATE_LIMITS = True
