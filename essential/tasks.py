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
def notify_async(user_object_id, user_content_type, notification_type,
                 acted_on_id=None, acted_on_content_type_id=None, **kwargs):
    user = ContentType.objects.get_for_id(user_content_type).get_object_for_this_type(pk=user_object_id)
    if user.get_handler() == kwargs.get('actor_handler', None):
        return

    acted_on = None
    if acted_on_id and acted_on_content_type_id:
        acted_on = ContentType.objects.get_for_id(acted_on_content_type_id).get_object_for_this_type(id=acted_on_id)
    getattr(__import__('essential.models', fromlist=['Notification']), 'Notification').objects.notify(
        user=user, notification_type=notification_type, acted_on=acted_on, **kwargs
    )


@app.task(name='notification_for_list_of_users')
def notify_list_async(model, method, method_kwargs, entity, notification_type,
                      acted_on_id=None, acted_on_content_type_id=None, **kwargs):
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

    acted_on = None
    if acted_on_id and acted_on_content_type_id:
        acted_on = ContentType.objects.get_for_id(acted_on_content_type_id).get_object_for_this_type(id=acted_on_id)

    for obj in result:
        user = getattr(obj, entity)
        if user.get_handler() == kwargs.get('actor_handler', None):
            pass
        getattr(__import__('essential.models', fromlist=['Notification']), 'Notification').objects.notify(
            user=user, notification_type=notification_type, acted_on=acted_on, **kwargs
        )


@app.task(name='notification_for_self_publication')
def notify_self_async(publication_id, notification_type,
                      acted_on_id=None, acted_on_content_type_id=None, **kwargs):
    publication = getattr(__import__(
        'publication.models', fromlist=['Publication']), 'Publication').objects.get(id=publication_id)

    kwargs.pop('template_key', None)
    kwargs.pop('verbose', None)

    if kwargs.get('self_verbose', None):
        kwargs.update({'verbose': kwargs['self_verbose']})
    elif kwargs.get('self_template_key', None):
        kwargs.update({'template_key': kwargs['self_template_key']})
    else:
        kwargs.update({'template_key': 'internal_publication'})

    acted_on = None
    if acted_on_id and acted_on_content_type_id:
        acted_on = ContentType.objects.get_for_id(acted_on_content_type_id).get_object_for_this_type(id=acted_on_id)
    getattr(__import__('essential.models', fromlist=['Notification']), 'Notification').objects.notify(
        user=publication, notification_type=notification_type, acted_on=acted_on, **kwargs
    )
