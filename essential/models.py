from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models


class NotificationManager(models.Manager):
    """ Manager for Notification model """

    def get_queryset(self):
        return super(NotificationManager, self).get_queryset()

    def get_notification(self, user):  # FIXME: Merge these 2 query without iter tools
        """
        returns all 'not notified' and only 5 'latest already notified'
        notifications are fetched from db
        """

        notified = self.get_queryset().filter(user=user, notified=True)[:5]
        not_notified = self.get_queryset().filter(user=user, notified=False)
        return not_notified

    def get_all_notification(self, user):
        """
        returns all the notifications
        which are ordered by timestamp (descending)
        """

        return self.get_queryset().filter(user=user).values_list('data', flat=True)

    def notify(self, user=None, write_up=None, notification_type=None):  # TODO: set json data info scheme
        """
        Call this method to save new notification.
        Checks if a similar notification already exists then increases the
        counter, else create a new entry.
        """

        if user and write_up and notification_type:
            try:
                notification = self.get_queryset().get(user=user,
                                                       write_up=write_up,
                                                       notification_type=notification_type,
                                                       notified=False)
            except Notification.DoesNotExist:
                self.create(user=user,
                            write_up=write_up,
                            data={},
                            notification_type=notification_type)
            else:
                notification.add_on_actor_count += 1
                notification.save()
        else:
            raise AssertionError("Invalid arguments - None type arguments")


class Notification(models.Model):
    """
    Stores User related Notifications.
    Publication Notification are stored by referring settings for every user-publication relation
    and are generated for so

    details in JSON -> image <url> of actor (user/publication), publication or not, text to show, redirect url

    JSON format -> for each notification data

    {'actor-image': '<image-url>', 'actor': 'actor-name', 'publication': 'True/False', 'contributor': 'True/False',
    'acted-on': 'writ-up name', 'level': 'success/info/warning/danger', 'redirect-url': '<url>'}

    actor, actor-image -> can be publisher or user
    all other details belong to the object acted on.

    type -> predefined and synchronised between front end and backend -
    'comment-like'
    'comment-dislike'
    'write-up like'
    'write-up dislike' ...

    A request will be needed on a notification click to mark it as notified. All new notifications will be marked as
    notified once the request is received. The 'notified url' will be encrypted using django signing with user_id and
    SALT as 'notification-opuslog'.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    write_up = models.ForeignKey('write_up.WriteUpCollection', on_delete=models.CASCADE)
    CHOICE = (('CO', 'Comment'),
              ('CR', 'Comment Reply'),
              ('CT', 'Comment Tagged'),
              ('UC', 'UpVote Comment'),
              ('DC', 'DownVote Comment'),
              ('UW', 'UpVote Write up'),
              ('DW', 'DownVote Write up'),
              )
    notification_type = models.CharField(max_length=2, choices=CHOICE)
    data = JSONField()
    add_on_actor_count = models.PositiveSmallIntegerField(default=0)
    notified = models.BooleanField(default=False)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-update_time']
