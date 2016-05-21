from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models


class NotificationManager(models.Manager):
    """
    Manager for Notification model

    get_notification ->  returns in format
    {'notification-new': [{...}, {...}, {...}, ...],
    'notification-old': [{...}, {...}, {...}, ...]}

    get_all_notification -> returns all the notifications in format
    [{...}, {...}, {...}, ...]
    which are ordered by timestamp (descending)
    """

    def get_queryset(self):
        return super(NotificationManager, self).get_queryset()

    def get_notification(self, user):  # TODO: can this be optimized?
        """ only 5 'latest' 'already notified' notifications are fetched from db """

        notified = self.get_queryset().filter(user=user, notified=True)[:5].values_list('data', flat=True)
        not_notified = self.get_queryset().filter(user=user, notified=False).values_list('data', flat=True)
        return {'notification-new': not_notified, 'notification-old': notified}

    def get_all_notification(self, user):
        return self.get_queryset().filter(user=user).values_list('data', flat=True)


class Notification(models.Model):
    """
    Stores User related Notifications.
    Publication Notification are stored by referring settings for every user-publication relation
    and are generated for so

    details in JSON -> image <url> of actor (user/publication), publication or not, text to show, redirect url

    JSON format -> for each notification

    {'actor-image': '<image-url>', 'actor': 'actor-name', 'publication': 'True/False', 'contributor': 'True/False',
    'acted-on': 'writ-up name', 'level': 'success/info/warning/danger', 'type': 'described below',
    'redirect-url': '<url>'}

    actor, actor-image -> can be publisher or user
    all other details belong to the object acted on.

    type -> predefined and synchronised between front end and backend -
    'comment-like'
    'comment-dislike'
    'write-up like'
    'write-up dislike' ...

    The API query will return ->
    {'notification-new': [{...}, {...}, {...}, ...],
    'notification-old': [{...}, {...}, {...}, ...],
    'notified': '<url>'}

    A request will be needed on a notification click to mark it as notified. All new notifications will be marked as
    notified once the request is received. The 'notified url' will be encrypted using django signing with user_id and
    SALT as 'notification-opuslog'.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # FIXME: Add write_up and notification type
    data = JSONField()
    notified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-timestamp']
