import datetime

from django.db.models import Q

from log.models import GroupWritingLockHistory


def validate_locked_group_writing_event():
    X_validation_timer = 5
    Y_validation_timer = 20

    current_time = datetime.datetime.now()
    target_time_x = current_time - datetime.timedelta(minutes=X_validation_timer)
    target_time_y = current_time - datetime.timedelta(minutes=Y_validation_timer)

    events = GroupWritingLockHistory.objects.filter(
        Q(last_x_request__lt=target_time_x) | Q(last_y_request__lt=target_time_y), status='A'
    ).select_related('article')

    for event in events:
        pass
