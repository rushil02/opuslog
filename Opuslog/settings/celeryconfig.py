from datetime import timedelta

from Opuslog.settings.common import TIME_ZONE



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

CELERYBEAT_SCHEDULE = {
    'validate_locked_group_writing_event': {
        'task': 'validate_locked_group_writing_event',
        'schedule': timedelta(minutes=2),
    },
}
