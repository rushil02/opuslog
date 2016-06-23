from __future__ import unicode_literals
import uuid
import time
import os

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
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
    flagged_entity = GenericRelation('moderator.FlaggedEntity', related_query_name='publication')
    group = GenericRelation('essential.Group', related_query_name='publication')

    objects = PublicationManager()

    def __unicode__(self):
        return self.name

    def set_administrator(self, user):
        return ContributorList.objects.create(contributer=user, publication=self, level='A')

    def get_handler_url(self):
        return reverse('publication:publication_details', kwargs={'publication_handler': self.handler})


class ContributorListQuerySet(models.QuerySet):
    def permission(self, acc_perm_code):
        return self.filter(Q(permissions__code_name=acc_perm_code) | Q(level='C'))

    def for_publication(self, publication):
        return self.get(publication=publication)


class ContributorListManager(models.Manager):
    def get_queryset(self):
        return ContributorListQuerySet(self.model, using=self._db)

    def get_contributor_for_publication_with_perm(self, publication, acc_perm_code):
        return self.get_queryset().permission(acc_perm_code).for_publication(publication)


class ContributorList(models.Model):
    """
    Every activity of publication is attached via this list and not to Publication model.
    On every new Publication creation, an entry will be created with owner set as the user.

    level -> Indicate just tags or designation for the user with relation to a publication. While settings
    do not depend on it. But every tag will have a default list of settings (not implemented at db level).
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


class PublicationActionHistory(models.Model):  # TODO: use with post_save
    """ Logs all acts by a Publication """
    # FIXME: publication and user can be replaced with contributorlist
    publication = models.ForeignKey('publication.Publication')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.publication.handler
