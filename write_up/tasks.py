import datetime

from django.db import transaction
from django.db.models import Q

from Opuslog.celery import app
from log.models import GroupWritingLockHistory
from write_up.models import GroupWriting


@app.task(name='validate_locked_group_writing_event', throws=(AssertionError,))
def validate_locked_group_writing_event():
    x_validation_timer = 5
    y_validation_timer = 20

    current_time = datetime.datetime.now()
    target_time_x = current_time - datetime.timedelta(minutes=x_validation_timer, seconds=30)
    target_time_y = current_time - datetime.timedelta(minutes=y_validation_timer, seconds=30)

    try:
        with transaction.atomic():
            GroupWriting.objects.filter(Q(groupwritinglockhistory__last_x_request__lt=target_time_x) | Q(
                groupwritinglockhistory__last_y_request__lt=target_time_y), groupwritinglockhistory__status='A').update(
                lock=False)

            GroupWritingLockHistory.objects.filter(
                Q(last_x_request__lt=target_time_x) | Q(last_y_request__lt=target_time_y), status='A'
            ).update(status='V')
    except Exception as e:
        raise AssertionError(e.message)
