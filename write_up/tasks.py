import datetime

from django.db.models import Q

from Opuslog.celery import app
from log.models import GroupWritingLockHistory


@app.task(name='validate_locked_group_writing_event', )
def validate_locked_group_writing_event():
    x_validation_timer = 5
    y_validation_timer = 20

    current_time = datetime.datetime.now()
    target_time_x = current_time - datetime.timedelta(minutes=x_validation_timer, seconds=30)
    target_time_y = current_time - datetime.timedelta(minutes=y_validation_timer, seconds=30)

    GroupWritingLockHistory.objects.filter(
        Q(last_x_request__lt=target_time_x) | Q(last_y_request__lt=target_time_y), status='A'
    ).update(article__lock=False, status='V')
