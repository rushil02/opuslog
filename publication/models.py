from __future__ import unicode_literals
import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from django.db import models
from django.conf import settings


class PublicationManager(models.Manager):
    def get_queryset(self):
        return super(PublicationManager, self).get_queryset()

    def create_publication(self, name):
        return self.get_queryset().create(name=name)


class Publication(models.Model):
    """
    Defines an actor entity as Publication. Relation to any user is satisfied
    using the model 'ContributorList' with relation attribute 'users'.
    """

    name = models.CharField(max_length=150)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    XP = models.BigIntegerField(default=0)
    money = models.BigIntegerField(default=0)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='contributors_in_publication',
                                   through='publication.ContributorList',
                                   through_fields=('publication', 'contributor'))
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
    request = GenericRelation('essential.Request', related_query_name='publication_request')

    objects = PublicationManager()

    def __unicode__(self):
        return self.name

    def set_administrator(self, user):
        return ContributorList.objects.create(contributer=user, publication=self, level='A')


class ContributorListQuerySet(models.QuerySet):
    def permission(self, acc_perm_code):
        return self.filter(Q(permissions__code_name=acc_perm_code) | Q(level='C'))

    def for_publication(self, publication_uuid):
        return self.select_related('publication').get(publication__uuid=publication_uuid)


class ContributorListManager(models.Manager):
    def get_queryset(self):
        return ContributorListQuerySet(self.model, using=self._db)

    def get_contributor_for_publication_with_perm(self, publication_uuid, acc_perm_code):
        return self.get_queryset().permission(acc_perm_code).for_publication(publication_uuid)


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
    LEVEL = (('A', 'Administrator'),  # TODO: Extend list of tags
             ('E', 'Editor'),
             ('N', 'Noob'),
             ('C', 'Creator'),
             )
    level = models.CharField(max_length=1, choices=LEVEL)
    permissions = models.ManyToManyField('essential.Permission', related_name='publication_permissions')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = ContributorListManager()

    class Meta:
        unique_together = ("publication", "contributor")

    def __unicode__(self):
        return "'%s' of '%s'" % (self.contributor, self.publication)

