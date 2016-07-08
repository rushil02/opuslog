from django.contrib.contenttypes.models import ContentType

# from write_up.models import WriteUp
from Opuslog.celery import app


def validate():
    """ Plugin ML model to validate engagement on a writeup here """
    return True


# def distribute_earnings():
#     write_ups = WriteUp.objects.filter()
#
#
# class ValidateWriteUpEngagement(object):
#     @staticmethod
#     def get_write_ups():
#         return WriteUp.objects.filter()
#
#     def __init__(self):
#         write_ups = self.get_write_ups()


@app.task(name='generate_async_notification')
def notify_async(user_object_id, user_content_type, notification_type, write_up_id=None, **kwargs):
    user = ContentType.objects.get_for_id(user_content_type).get_object_for_this_type(pk=user_object_id)
    if user.get_handler() == kwargs.get('actor_handler', None):
        pass

    write_up = None
    if write_up_id:
        write_up = getattr(__import__('write_up.models', fromlist=['WriteUp']), 'WriteUp').objects.get(id=write_up_id)
    getattr(__import__('essential.models', fromlist=['Notification']), 'Notification').objects.notify(
        user=user, notification_type=notification_type, write_up=write_up, **kwargs
    )


@app.task(name='generate_async_notification_for_list_of_users')
def notify_list_async(model, method, method_kwargs, entity, notification_type, write_up_id=None, **kwargs):
    """
    Used when you need to send a notification to a list of users/publication
    model -> example 'essential.Notification'
    method -> queryset filter, etc
    method_kwargs -> {..., ..., } dictionary used as arguments
    result -> should be an iterable of users or publication objects
    """

    model = model.split('.')
    klass = getattr(__import__(model[0] + '.models', fromlist=[model[1]]), model[1])
    result = getattr(klass.objects, method)(**method_kwargs)

    write_up = None
    if write_up_id:
        write_up = getattr(__import__('write_up.models', fromlist=['WriteUp']), 'WriteUp').objects.get(id=write_up_id)

    for obj in result:
        user = getattr(obj, entity)
        if user.get_handler() == kwargs.get('actor_handler', None):
            pass

        getattr(__import__('essential.models', fromlist=['Notification']), 'Notification').objects.notify(
            user=user, notification_type=notification_type, write_up=write_up, **kwargs
        )
