"""
Actor and write_up relationship:
A user or publication can create multiple write ups.
There can be numerous contributors for each write_up irrespective
of weather the contributor itself is a publisher or user.
Therefore,
    GFK(user, publisher) -> ContributorList <- write_up
ContributorList registers the creator of write_up as primary owner
with all the rights and permissions.
Therefore every and any relationship between user/publication and write_up
is held by the ContributorList.
This method also supports the concept of guest writer per write_up for
publications. While it can completely handle multiple publication contribution on a
write up, it's more of a question if the developer wants it or not.

The owner (publisher/user) can choose to set access
level (show-in-their-feed/edit/delete) for each contributor (user/publisher).

Problem - a user can belong to 2 publications, which will get him/her extra gains
          than it should. Resolution of such a behaviour is hectic at DBMS level.
          A warning will be generated to both the sides in such scenario.
        - Current scheme allows a publication and a user (of same publication) to
          be contributor for same write_up. This has to be validated to avoid such
          a case.

It is important to carefully describe a single write_up which works as a 'datum'
for Engagement Algorithm to calculate XP and money. Net Evaluation will be with
respect to this datum and not a user or publication (money/XP earned by an actor).
Those are for user representation purposes only and do not provide any
significant evaluation for the system.

Write_up types and BaseDesign relationship: (defines datum)
Since each type of write_up determines a different relationship
with BaseDesign, an intermediary table is required to establish such
relationship. BaseDeign will never be directly connected with WriteUp.

"""
from __future__ import unicode_literals

import uuid
import os
import time
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

from essential.models import Permission
from publication.models import Publication


def get_file_path(instance, filename):
    path = 'Covers/' + instance.get_collection_type_display() + time.strftime('/%Y/%m/%d/')
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.uuid, ext)
    return os.path.join(path, filename)


class WriteUpManager(models.Manager):
    def create_writeup(self, title, collection_type, description, cover):
        return self.get_queryset().create(title=title, collection_type=collection_type, description=description,
                                          cover=cover)


class WriteUp(models.Model):
    """
    A Write Up can belong (primary owner) to a user, a publication but not both.
    This table acts as a complete index of a library without any reference to its owner.

    Relation to any user is satisfied using the model 'ContributorList' with relation
    attribute 'users'. Multiple ownership of a write up is dealt via the same aforementioned model.
    On every new write up creation, an entry will be created in aforementioned model with owner set
    as the user.

    Collection will be composed of units. It can be a book or Magazine. By default for every user
    there will be a write up extending to a collection  marked as 'Independent'.
    user ->  holds the info who created the writeup
    up_votes, down_votes, comments -> counters to avoid aggregate querying
    """

    title = models.CharField(max_length=250)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    TYPE = (('B', 'Book'),
            ('M', 'Magazine'),
            ('I', 'Independent Article'),
            ('L', 'LiveWriting'),
            ('G', 'GroupWriting'),
            )
    collection_type = models.CharField(max_length=1, choices=TYPE)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    up_votes = models.PositiveIntegerField(default=0)
    down_votes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('essential.Tag')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    for_requests = GenericRelation('essential.Request', content_type_field='request_for_content_type',
                                   object_id_field='request_for_object_id', related_query_name='write_up')
    flagged_entity = GenericRelation('moderator.FlaggedEntity', related_query_name='write_up')

    group = models.ForeignKey('essential.Group')

    objects = WriteUpManager()

    class CustomMeta:
        permission_list = [
            {'name': 'Can Edit Write Up', 'code_name': 'can_edit',
             'help_text': 'Allow contributor to edit Write up',
             'for': 'W'},
            {'name': 'Can Create Write Up', 'code_name': 'can_create_write_up',
             'help_text': 'Allow contributor to create Write up',
             'for': 'P'},
        ]

    def __unicode__(self):
        return self.title

    def set_owner(self, owner):  # fixme: add all writeup permissions to owner
        contributor = ContributorList.objects.create_contributor(owner, write_up=self, is_owner=True, share_XP=100,
                                                                 share_money=100)
        write_up_permissions = Permission.objects.get_permissions_for_write_up()
        contributor.permissions.add(*write_up_permissions)
        return contributor

    def create_write_up_profile(self, user):
        return WriteupProfile.objects.create(write_up=self, created_by=user)

    def add_contributor(self, contributor, share_xp, share_money):
        return ContributorList.objects.create_contributor(contributor, write_up=self, share_XP=share_xp,
                                                          share_money=share_money)

    def get_all_contributors(self):  # FIXME: exclude removed contributors
        return self.contributorlist_set.get_all_contributors_for_write_up()

    def create_write_up_handler(self, **kwargs):
        method_name = 'create_' + self.collection_type.lower()
        method = getattr(self, method_name)
        method(**kwargs)

    def get_handler_redirect_url(self):
        """
        Returns URL for creating specific type of write_up. for eg:
        Book -> Url for displaying all chapters page
        Magazine -> Url for displaying all articles page
        Independent article -> Url for editing/displaying article
        Similarly for group and live writing.
        """

        redirect_url = {
            'B': '',
            'M': '/edit_magazine_chapters/',
            'I': '/edit_article/',
            'L': '',
            'G': '',
        }
        return redirect_url.get(self.collection_type)

    def create_b(self, **kwargs):
        pass

    def create_m(self, **kwargs):
        pass

    def create_i(self, **kwargs):
        contributor = kwargs.get('contributor')
        base_design = BaseDesign.objects.create()
        unit = Unit.objects.create(write_up=self, text=base_design)
        unit.add_unit_contributor(contributor)

    def create_l(self, **kwargs):
        base_design = BaseDesign.objects.create()
        LiveWriting.objects.create(write_up=self, text=base_design)

    def create_g(self, **kwargs):
        GroupWriting.objects.create(write_up=self)

    def get_all_chapters(self):
        return self.collectionunit_set.all().select_related('article').order_by('sort_id')

    def get_owner(self):
        return self.contributorlist_set.get(is_owner=True)

    def get_chapter_from_index(self, i):
        return self.get_all_chapters().select_related('article__text')[i - 1]


class WriteupProfile(models.Model):
    write_up = models.OneToOneField(WriteUp)
    XP = models.PositiveIntegerField(default=0)
    money = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    last_assessed_time = models.DateTimeField(default=datetime.utcfromtimestamp(0))


class ContributorListQuerySet(models.QuerySet):
    def permission(self, permission_list):
        permission_qs = self
        for permission in permission_list:
            permission_qs = permission_qs.filter(permissions__code_name=permission)
        return permission_qs

    def owner(self):
        return self.filter(is_owner=True)

    def for_write_up(self, write_up_uuid, collection_type=None):
        if collection_type:
            return self.select_related('write_up').get(write_up__uuid=write_up_uuid,
                                                       write_up__collection_type=collection_type)
        else:
            return self.select_related('write_up').get(write_up__uuid=write_up_uuid)


class ContributorListManager(models.Manager):
    def get_queryset(self):
        return ContributorListQuerySet(self.model, using=self._db)

    def get_contributor_for_writeup_with_perm(self, write_up_uuid, permission_list, collection_type=None):
        return self.get_queryset().permission(permission_list).for_write_up(write_up_uuid, collection_type)

    def create_contributor(self, contributor, write_up, is_owner=False, share_XP=None, share_money=None):
        return self.get_queryset().create(contributor=contributor, write_up=write_up, is_owner=is_owner,
                                          share_XP=share_XP, share_money=share_money)

    def get_owner_for_permission(self, write_up_uuid, collection_type=None):
        return self.get_queryset().owner().for_write_up(write_up_uuid, collection_type)

    def get_all_contributors_for_write_up(self):
        return self.get_queryset().all().prefetch_related('permissions', 'contributor')


# TODO: create celery task to validate and update per write_up engagement based XP/money for user
class ContributorList(models.Model):
    """
    It holds the List of Contributor for each write up, therefore relation between any
    user/publication entity and writeup entity is via this table. It is an intermediary
    table for user/publication to writeup relation. The primary creator/owner of a writeup
    is defined and marked using the 'is_owner' field.

    Money or XP earned by a user or publication via a write_up is determined by this table.

    permission_level determines the permitted interaction level between a contributor and
    write up. Once set, it cannot be changed after a user accepts to contribute in the write up.
    """

    LIMIT = models.Q(app_label='publication',
                     model='publication') | models.Q(app_label='user_custom',
                                                     model='user')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                     related_name='contributed_write_ups')
    object_id = models.PositiveIntegerField()
    contributor = GenericForeignKey('content_type', 'object_id')
    is_owner = models.BooleanField(default=False)
    share_XP = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    permissions = models.ManyToManyField('essential.Permission', related_name='writeup_permissions')
    write_up = models.ForeignKey(WriteUp)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = ContributorListManager()

    class Meta:
        unique_together = ("write_up", "object_id", "content_type")

    def __unicode__(self):
        return "'%s' of '%s'" % (self.contributor, self.write_up)

    def get_contributor_handler(self):
        if isinstance(self.contributor, Publication):
            return self.contributor.handler
        elif isinstance(self.contributor, get_user_model()):
            return self.contributor.username


class BaseDesign(models.Model):
    """
    Directly patched to Revision History Model.
    Anything that is saved to this model is revised in a separate model.
    For revisions - Save using method 'save_with_rev'
    """

    text = models.TextField()
    update_time = models.DateTimeField(auto_now=True)

    def save_with_revision(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        title = kwargs.pop('title', None)
        RevisionHistory.objects.create(user=user, parent=self, title=title, text=self.text)
        super(BaseDesign, self).save(*args, **kwargs)

    def autosave_with_revision(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        try:
            last_entry = RevisionHistory.objects.order_by('-create_time').defer('text') \
                .filter(parent=self,
                        title__startswith='AUTOSAVE')[0]
        except IndexError:
            title = 'AUTOSAVE-' + str(datetime.now())
            RevisionHistory.objects.create(user=user, parent=self, title=title, text=self.text)
        else:
            last_entry.title = 'AUTOSAVE-' + str(datetime.now())
            last_entry.text = self.text
            last_entry.save()
        super(BaseDesign, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)


class Unit(models.Model):
    """ A chapter/article can be related directly to a writeup or via a book/magazine. """

    write_up = models.OneToOneField(WriteUp, null=True)
    text = models.OneToOneField(BaseDesign)
    title = models.CharField(max_length=250, null=True, blank=True)

    def add_unit_contributor(self, contributor):
        return self.unitcontributor_set.create(contributor=contributor)


class UnitContributor(models.Model):
    """ Holds the creators for each Chapter/Article in a write up. """

    article = models.ForeignKey(Unit)
    contributor = models.ForeignKey(ContributorList)


class CollectionUnit(models.Model):
    """
    It is the intermediary table for Write up type 'Magazine' and its units
    'article'. A Magazine can have multiple articles. An article's primary
    can be another writeup from which the same is imported, else it can be
    implicit to the Magazine.
    """

    magazine = models.ForeignKey(WriteUp)
    article = models.ForeignKey(Unit)
    CHOICES = (('I', 'Implicit'),
               ('E', 'Explicit'))
    relationship = models.CharField(max_length=1, choices=CHOICES)
    sort_id = models.PositiveSmallIntegerField()
    share_XP = models.DecimalField(max_digits=5, decimal_places=5, null=True, blank=True)
    share_money = models.DecimalField(max_digits=5, decimal_places=5, null=True, blank=True)


class LiveWriting(models.Model):
    """
    No Revision History
    Save to same BaseDesign object repetitively
    closed group -> if only restricted group of people should be part of the event, then True
    """

    write_up = models.OneToOneField(WriteUp)
    text = models.OneToOneField(BaseDesign)
    closed_group = models.BooleanField(default=False)
    closed_group_users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.write_up


class GroupWriting(models.Model):
    """
    For Group writing events. Only for users and not Publications.
    Sequentially users can add on to a story/article.
    Concurrent development is to be avoided as it violates the concept (until stories can be branched).
    No Revision History
    Locking mechanism to avoid concurrent development: While the user is actively extending the
    article, every 'X' min. make an api call to keep the object locked. After 'Y' min ask the user to
    fill captcha to reset 'Y' timer. If either X or Y exceeds, unlock the table back. and make the current session void.

    closed group -> if only restricted group of people should be part of the event, then True
    """

    write_up = models.OneToOneField(WriteUp)
    closed_group = models.BooleanField(default=False)
    closed_group_users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    active = models.BooleanField(default=True)
    lock = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.write_up


class GroupWritingText(models.Model):
    """ Stores all the data filled by multiple users for single group written article.
    Once written Text is non editable unless it is latest and the lock is open """

    article = models.ForeignKey(GroupWriting)
    sequence = models.PositiveSmallIntegerField()
    writer = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.OneToOneField(BaseDesign)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.article


class RevisionHistory(models.Model):
    """
    Stores textual revision history for BaseDesign model.
    Sequence of revision is determined by update_time.
    """

    parent = models.ForeignKey(BaseDesign)
    user = models.ForeignKey(ContributorList)
    title = models.CharField(max_length=250, null=True, blank=True)
    text = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "'%s', revision at: '%s'" % (self.parent, self.update_time)
