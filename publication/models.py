from __future__ import unicode_literals
import uuid
import time
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings


def get_logo_file_path(instance, filename):
    path = 'Publication/Logo' + time.strftime('/%Y/%m/%d/')
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.uuid, ext)
    return os.path.join(path, filename)


def get_background_file_path(instance, filename):
    path = 'PublicationEnvironment/Background' + time.strftime('/%Y/%m/%d/')
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.publication.uuid, ext)
    return os.path.join(path, filename)


class PublicationManager(models.Manager):
    def get_queryset(self):
        return super(PublicationManager, self).get_queryset()

    def create_publication(self, name):
        return self.get_queryset().create(name=name)


class Publication(models.Model):  # TODO create default group for each publication
    """
    Defines an actor entity as Publication. Relation to any user is satisfied
    using the model 'ContributorList' with relation attribute 'users'.

    created_by stores the owner of publication
    """

    name = models.CharField(max_length=150)
    handler = models.CharField(
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    XP = models.BigIntegerField(default=0)
    money = models.BigIntegerField(default=0)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='contributors_in_publication',
                                   through='publication.ContributorList',
                                   through_fields=('publication', 'contributor'))
    logo = models.ImageField(upload_to=get_logo_file_path, null=True, blank=True)
    tags = models.ManyToManyField('essential.Tag')
    subscribers_num = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    votes = GenericRelation('engagement.VoteWriteUp', related_query_name='publication')
    comments = GenericRelation('engagement.Comment', related_query_name='publication')
    vote_comments = GenericRelation('engagement.VoteComment', related_query_name='publication')
    subscribed = GenericRelation('engagement.Subscriber', related_query_name='publication_subscribed')
    subscriptions = GenericRelation('engagement.Subscriber', 'object_id_2', 'content_type_2',
                                    related_query_name='publication_subscriptions')
    contribution = GenericRelation('write_up.ContributorList', related_query_name='publication')
    for_requests = GenericRelation('essential.Request', content_type_field='request_for_content_type',
                                   object_id_field='request_for_object_id',
                                   related_query_name='publication_for_request')
    sent_requests = GenericRelation('essential.Request', content_type_field='request_from_content_type',
                                    object_id_field='request_from_object_id',
                                    related_query_name='publication_sent_request')
    received_requests = GenericRelation('essential.Request', content_type_field='request_to_content_type',
                                        object_id_field='request_to_object_id',
                                        related_query_name='publication_received_request')
    threads = GenericRelation('messaging_system.ThreadMember', related_query_name='publication')
    created_threads = GenericRelation('messaging_system.Thread', related_query_name='publication')
    flagged_entity = GenericRelation('moderator.FlaggedEntity', related_query_name='publication')
    group = GenericRelation('essential.Group', related_query_name='publication')

    objects = PublicationManager()

    def __unicode__(self):
        return self.name

    def set_administrator(self, user):
        return ContributorList.objects.create(contributer=user, publication=self, level='A')

    def get_handler(self):
        return self.handler

    def get_handler_url(self):
        return reverse('publication:publication_details', kwargs={'pub_handler': self.handler})

    def get_all_contributors_as_users_with_permission(self, permission_list):
        return self.contributorlist_set.get_all_contributors_with_permission(permission_list)


class ContributorListQuerySet(models.QuerySet):
    def permission(self, permission_list):
        permission_qs = self
        for permission in permission_list:
            permission_qs = permission_qs.filter(permissions__code_name=permission)
        return permission_qs

    # def owner(self):
    #     return self.filter(publication__created_by=F('contributor'))

    def for_publication(self, publication_handler, user):
        return self.select_related('publication').get(publication__handler=publication_handler, contributor=user)


class ContributorListManager(models.Manager):
    def get_queryset(self):
        return ContributorListQuerySet(self.model, using=self._db)

    def get_contributor_for_publication_with_perm(self, publication_handler, permission_list, user):
        return self.get_queryset().permission(permission_list).for_publication(publication_handler, user)

    def get_all_contributors_with_permission(self, permission_list):
        return self.get_queryset().permission(permission_list).select_related('contributor')


class ContributorList(models.Model):
    """
    Every activity of publication is attached via this list and not to Publication model.
    On every new Publication creation, an entry will be created with owner set as the user.
    'Owner' is just a display designation which can be modified by the user.

    permission -> holds all the Publication level permissions
    """

    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contributed_publications')
    publication = models.ForeignKey(Publication)
    share_XP = models.DecimalField(default=0.0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0.0, max_digits=8, decimal_places=5)
    PREDEFINED = ('Owner', 'Administrator', 'Editor', 'Creator')  # TODO: Assign default permissions in View
    designation = models.CharField(max_length=20, default=PREDEFINED[3])
    permissions = models.ManyToManyField('essential.Permission', related_name='publication_permissions')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    activity = GenericRelation('admin_custom.ActivityLog', related_query_name='contributor')

    objects = ContributorListManager()

    class Meta:
        unique_together = ("publication", "contributor")

    def __unicode__(self):
        return "'%s' of '%s'" % (self.contributor, self.publication)


class PublicationEnvironment(models.Model):
    """ Defines the chosen Workspace Environment for users in a Publication. """

    publication = models.OneToOneField(Publication)
    CHOICE = (('1', 'Dark Theme'),
              ('2', 'Light theme'),
              )
    theme = models.CharField(max_length=1, choices=CHOICE)
    background = models.ImageField(upload_to=get_background_file_path, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)
