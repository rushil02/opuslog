from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.conf import settings


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

        return self.get_queryset().filter(user=user)

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


class Notification(models.Model):  # TODO: make notification system more dumb
    """
    Stores User related Notifications.
    Publication Notification are stored by referring settings for every
    user-publication relation and are generated for so.

    details in JSON -> image <url> of actor (user/publication),
                       publication or not, text to show, redirect url

    JSON format -> for each notification data

    {'actor-image': '<image-url>', 'actor': 'actor-name',
    'publication': 'True/False', 'contributor': 'True/False',
    'acted-on': 'writ-up name', 'level': 'success/info/warning/danger',
    'redirect-url': '<url>'}

    actor, actor-image -> can be publisher or user
    all other details belong to the object acted on.

    type -> predefined and synchronised between front end and backend -
    'comment-like'
    'comment-dislike'
    'write-up like'
    'write-up dislike' ...

    A request will be needed on a notification click to mark it as notified.
    All new notifications will be marked as notified once the request is
    received. The 'notified url' will be encrypted using django signing with
    user_id and SALT as 'notification-opuslog'.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    write_up = models.ForeignKey('write_up.WriteUp', on_delete=models.CASCADE)
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


class Tag(models.Model):
    """
    Tags are defined on a writeup/Publication using a many to many relation
    Primary tags are added manually by the developer and at least one such
    tag is necessary on a writeup/Publication.
    Secondary tags are populated by user entries. They are not compulsory on
    a writeup/Publication but are used by the recommendation system for
    better results.
    """

    name = models.CharField(max_length=30)
    TAG_TYPE = (('P', 'Primary'),
                ('S', 'Secondary')
                )
    tag_type = models.CharField(max_length=1)
    create_time = models.DateTimeField(auto_now_add=True)


class Group(models.Model):
    """
    Works as folders or categorising write ups internally for a creator entity.
    Publication additionally can assign permissions over this categorisation
    to its contributor.
    """

    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    entity = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('content_type', 'object_id', 'name')


class GroupContributor(models.Model):
    """
    Intermediary table for defining write up level permissions to each
    contributor of a publication.
    """

    group = models.ForeignKey(Group)
    contributor = models.ForeignKey('publication.ContributorList')
    permission = models.ManyToManyField('essential.Permission')

    class Meta:
        unique_together = ('group', 'contributor')


class Permission(models.Model):
    """
    Defines permission for each contributor in Writeup/Publication.
    """

    name = models.CharField(max_length=100)
    help_text = models.CharField(max_length=250, null=True, blank=True)
    code_name = models.CharField(max_length=30)
    FOR_TYPE = (('W', 'Write up'),
                ('P', 'Publication'),
                )
    permission_type = models.CharField(max_length=1, choices=FOR_TYPE)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='contributor_permission')
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.code_name


class Request(models.Model):
    """ Request by or for a user/publication to contribute in a Publication/Writeup"""

    LIMIT = models.Q(app_label='publication',
                     model='publication') | models.Q(app_label='write_up',
                                                     model='writeup')
    request_for_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                 related_name='request_for')
    request_for_object_id = models.PositiveIntegerField()
    request_for = GenericForeignKey('request_for_content_type', 'request_for_object_id')

    LIMIT = models.Q(app_label='publication',
                     model='publication') | models.Q(app_label='user_custom',
                                                     model='user')
    request_from_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                  related_name='request_from')
    request_from_object_id = models.PositiveIntegerField()
    request_from = GenericForeignKey('request_from_content_type', 'request_from_object_id')

    LIMIT = models.Q(app_label='publication',
                     model='publication') | models.Q(app_label='user_custom',
                                                     model='user')
    request_to_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                related_name='request_to_')
    request_to_object_id = models.PositiveIntegerField()
    request_to = GenericForeignKey('request_to_content_type', 'request_to_object_id')
    STATUS = (
        ('A', 'Accepted'),
        ('R', 'Rejected'),
        ('P', 'Pending'),
    )
    status = models.CharField(max_length=1, choices=STATUS)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
