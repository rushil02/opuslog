from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.conf import settings

from admin_custom.models import ActivityLog


class NotificationManager(models.Manager):
    """ Manager for Notification model """

    def get_queryset(self):
        return super(NotificationManager, self).get_queryset()

    def get_notification(self, user):  # FIXME: Merge these 2 query without iter tools, Tiwari batayega
        """
        returns all 'not notified' and only 5 'latest already notified'
        notifications are fetched from db
        """

        old = self.get_queryset().filter(user=user, notified=True)[:5]
        new = self.get_queryset().filter(user=user, notified=False)
        return new

    def get_all_notification(self, user):
        """
        returns all the notifications
        which are ordered by timestamp (descending)
        """

        return self.get_queryset().filter(user=user)

    def create_new_notification(self, user, notification_type, template_key, write_up=None, **kwargs):
        context = {
            'image': kwargs.pop('image_url', None),
            'level': kwargs.pop('level', 'info'),
            'redirect-url': kwargs.pop('redirect_url', None),
        }

        notification = Notification(user=user,
                                    write_up=write_up,
                                    data=kwargs,
                                    notification_type=notification_type)

        return notification.save(template_key=template_key, verbose=kwargs.get('verbose', None), context=context)

    def notify(self, user, notification_type, write_up=None, **kwargs):
        """
        Call this method to save new notification.
        Checks if a similar notification already exists then increases the
        counter, else create a new entry.
        """

        if user and notification_type:
            url_append = kwargs.get('redirect_url', None)
            if isinstance(user, get_user_model()):
                self._notify(user, notification_type, write_up, **kwargs)
            elif isinstance(user, getattr(__import__('publication.models', fromlist=['Publication']), 'Publication')):
                perm = ['receive_Notification']
                perm.extend(kwargs.pop('permissions', []))
                contributors = user.get_all_contributors_as_users_with_permission(perm)
                acted_contributor = kwargs.get('contributor', None)
                if url_append:
                    kwargs['redirect_url'] = '/pub/' + user.handler + kwargs['redirect_url']
                for publication_user in contributors:
                    if not publication_user.contributor.username == acted_contributor:
                        self._notify(publication_user.contributor, notification_type, write_up, **kwargs)
            else:
                ActivityLog.objects.create_log(
                    level='C', message="Notification user object is neither of model 'User' nor 'Publication'",
                    act_type="Error in creating notification", user=str(user), notification_type=notification_type,
                    request=None, view='NotificationManager.notify', arguments={'kwargs': kwargs},
                )
        else:
            ActivityLog.objects.create_log(
                level='C', message="User or Notification type not given",
                act_type="Error in creating notification", user=str(user),
                notification_type=notification_type, request=None, view='NotificationManager.notify',
                arguments={'kwargs': kwargs},
            )

    def _notify(self, user, notification_type, write_up=None, **kwargs):
        template_key = kwargs.pop('template_key', 'many')
        try:
            if template_key == 'single' or kwargs.get('verbose', None):
                raise Notification.DoesNotExist
            notification = self.get_queryset().get(user=user,
                                                   write_up=write_up,
                                                   notification_type=notification_type,
                                                   notified=False)
        except Notification.DoesNotExist:
            if template_key == 'many':
                template_key = 'single'
            self.create_new_notification(user, notification_type, template_key, write_up, **kwargs)
        else:
            notification.add_on_actor_count += 1
            notification.save(template_key=template_key, verbose=kwargs.get('verbose', None))


class Notification(models.Model):
    """
    Stores User related Notifications.
    Publication Notification are stored by referring settings for every
    user-publication relation and are generated for so.

    details in JSON -> image <url> of actor (user/publication),
                       publication or not, text to show, redirect url

    JSON format -> for each notification data

    {'image': '<image-url>', 'actor': 'actor-handler',
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

    data = {
        'actor': kwargs.pop('actor_handler', None),
        'contributor': kwargs.pop('contributor', None),
        'acted-on': kwargs.pop('acted_on', None),
        'extra': ...,
        ...
        }
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    write_up = models.ForeignKey('write_up.WriteUp', null=True, blank=True)

    CHOICE = (
        ('CO', 'Comment'),
        ('CR', 'Comment Reply'),
        ('CT', 'Comment Tagged'),
        ('UC', 'UpVote Comment'),
        ('DC', 'DownVote Comment'),
        ('UW', 'UpVote Write up'),
        ('DW', 'DownVote Write up'),
        ('NT', 'New Thread'),
        ('UT', 'Update Thread subject'),
        ('RL', 'Request Accept/Deny'),  # TODO: append notification id in frontend to its url
    )
    display_details = {
        'CO': {'single':
                   {'template': '{} commented on your creation {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many': {'template': '{} and {} others commented on your creation {}',
                        'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'CR': {'single':
                   {'template': '{} replied to your comment on {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many':
                   {'template': '{} and {} others replied to your comment on {}',
                    'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'CT': {'single':
                   {'template': '{} tagged you in a comment on {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'image': "",
               },
        'UC': {'single':
                   {"template": '{} up voted your comment on {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many': {'template': '{} and {} others up voted your comment on {}',
                        'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'DC': {'single':
                   {'template': '{} down voted your comment on {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many': {'template': '{} and {} others down voted your comment on {}',
                        'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'UW': {'single':
                   {'template': '{} up voted your creation {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many': {'template': '{} and {} others up voted your comment on {}',
                        'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'DW': {'single':
                   {'template': '{} down voted your creation {}',
                    'args': [{'data': 'actor'}, 'write_up']},
               'many': {'template': '{} and {} others down voted your creation {}',
                        'args': [{'data': 'actor'}, 'add_on_actor_count', 'write_up']},
               'image': "",
               },
        'NT': {'single':
                   {'template': "'{} created a new thread with subject '{}'",
                    'args': [{'data': 'actor'}, {'data': 'acted-on'}, ]},
               'image': "",
               },
        '`UT`': {'single':
                     {'template': "'{}' edited the Thread of subject '{}' to '{}'",
                      'args': [{'data': 'actor_handler'}, {'data': 'old_subject'}, {'data': 'new_subject'}, ]},
                 'internal_publication':
                     {'template': "'{}' of Publication '{}' edited the Thread of subject '{}' to '{}'",
                      'args': [{'data': 'contributor'}, {'data': 'actor'}, {'data': 'extra'}, {'data': 'acted-on'}, ]},
                 'image': "",
                 },
    }
    notification_type = models.CharField(max_length=2, choices=CHOICE)

    data = JSONField()
    context = JSONField()
    add_on_actor_count = models.PositiveSmallIntegerField(default=0)
    notified = models.BooleanField(default=False)
    verbose = models.CharField(max_length=100, blank=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    class CustomMeta:
        permission_list = [
            {'name': 'Can receive Notification', 'code_name': 'receive_Notification',
             'help_text': 'Allow contributor to receive Notification'},
        ]

    class Meta:
        ordering = ['-update_time']

    def save(self, *args, **kwargs):
        template_key = kwargs.pop('template_key', 'single')
        verbose = kwargs.pop('verbose', None)
        self.context = kwargs.pop('context')
        if not self.context['image']:
            self.context['image'] = self.get_default_image()
        self.verbose = verbose if verbose else self.get_verbose(self.notification_type, template_key)
        super(Notification, self).save(*args, **kwargs)

    def get_verbose(self, notification_type, template_key):
        verbose_handler = self.display_details[notification_type][template_key]
        template = verbose_handler['template']
        template_args = verbose_handler['args']
        args = []
        for arg in template_args:
            if isinstance(arg, dict):
                args.append(self.data[arg['data']])
            else:
                args.append(getattr(self, arg))
        return template.format(*args)

    def get_default_image(self):
        foo = self.display_details
        return ""


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


class GroupManager(models.Manager):
    def get_other_groups(self):
        return self.get_queryset().filter(contributed_group=False)


class Group(models.Model):
    """
    Works as folders or categorising write ups internally for a creator entity.
    Publication additionally can assign permissions over this categorisation
    to its contributor.
    Contributed Group field is true for groups storing the contributed write ups for a publication
    """

    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=100)
    contributed_group = models.BooleanField(default=False)

    objects = GroupManager()

    class Meta:
        unique_together = ('content_type', 'object_id', 'name')

    def __unicode__(self):
        return self.name

    def get_contributor_with_perm(self, perm_list, contributor):
        return self.groupcontributor_set.get_contributor_for_group_with_perm(perm_list, contributor)


class GroupContributorQuerySet(models.QuerySet):
    def permission(self, permission_list):
        permission_qs = self
        for permission in permission_list:
            permission_qs = permission_qs.filter(permissions__code_name=permission)
        return permission_qs

    def for_contributor(self, contributor):
        return self.get(contributor=contributor)


class GroupContributorManager(models.Manager):
    def get_queryset(self):
        return GroupContributorQuerySet(self.model, using=self._db)

    def get_contributor_for_group_with_perm(self, permission_list, contributor):
        return self.get_queryset().permission(permission_list).for_contributor(contributor)


class GroupContributor(models.Model):
    """
    Intermediary table for defining write up level permissions to each
    contributor of a publication.
    """

    group = models.ForeignKey(Group)
    contributor = models.ForeignKey('publication.ContributorList')
    permissions = models.ManyToManyField('essential.Permission')

    objects = GroupContributorManager()

    class Meta:
        unique_together = ('group', 'contributor')


class PermissionManager(models.Manager):
    def get_permissions_for_write_up(self):
        return self.get_queryset().filter(permission_type='W')


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

    objects = PermissionManager()

    def __unicode__(self):
        return self.code_name


class RequestLog(models.Model):
    """
    - Request by or for a user/publication to contribute in a Publication/Writeup
    - Request by a user/Publication to a user/Publication to join in on a Thread as its member
    """

    LIMIT = models.Q(
        app_label='publication',
        model='publication'
    ) | models.Q(
        app_label='write_up',
        model='writeup'
    ) | models.Q(
        app_label='messaging_system',
        model='thread'
    )
    request_for_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                 related_name='request_for')
    request_for_object_id = models.PositiveIntegerField()
    request_for = GenericForeignKey('request_for_content_type', 'request_for_object_id')

    LIMIT = models.Q(
        app_label='publication',
        model='publication'
    ) | models.Q(
        app_label='user_custom',
        model='user'
    )
    request_from_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                  related_name='request_from')
    request_from_object_id = models.PositiveIntegerField()
    request_from = GenericForeignKey('request_from_content_type', 'request_from_object_id')

    LIMIT = models.Q(
        app_label='publication',
        model='publication'
    ) | models.Q(
        app_label='user_custom',
        model='user'
    )
    request_to_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                                related_name='request_to_')
    request_to_object_id = models.PositiveIntegerField()
    request_to = GenericForeignKey('request_to_content_type', 'request_to_object_id')
    STATUS = (
        ('A', 'Accepted'),
        ('R', 'Rejected'),
        ('P', 'Pending'),
    )
    status = models.CharField(max_length=1, choices=STATUS, default='P')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('request_for_content_type', 'request_for_object_id',
                           'request_to_content_type', 'request_to_object_id',
                           'status',
                           )
