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

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.conf import settings


def get_file_path(instance, filename):
    if instance.collection_type == 'B':
        path = 'Covers/Book' + time.strftime('/%Y/%m/%d/')
    elif instance.collection_type == 'M':
        path = 'Covers/Magazine' + time.strftime('/%Y/%m/%d/')
    else:
        return False

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.uuid, ext)
    return os.path.join(path, filename)


class WriteUpManager(models.Manager):
    def get_queryset(self):
        return super(WriteUpManager, self).get_queryset()

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

    title = models.CharField(max_length=250, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    TYPE = (('B', 'Book'),
            ('M', 'Magazine'),
            ('I', 'Independent'),
            ('L', 'LiveWriting'),
            ('G', 'GroupWriting'),
            )
    collection_type = models.CharField(max_length=1, choices=TYPE)
    description = models.TextField()
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    up_votes = models.PositiveIntegerField(default=0)
    down_votes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    XP = models.PositiveIntegerField(default=0)
    money = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('essential.Tag')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = WriteUpManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        exists = self.pk
        owner = kwargs.pop('owner')
        super(WriteUp, self).save(*args, **kwargs)
        if not exists:
            self.set_owner(owner)

    def set_owner(self, owner):
        return ContributorList.objects.create(contributer=owner, is_owner=True, level='E', write_up=self)

    def add_contributor(self, contributor, level, share_XP, share_money):
        return ContributorList.objects.create(contributer=contributor, permission_level=level, share_XP=share_XP,
                                              share_money=share_money, write_up=self)

        # def remove_contributor(self, contributor):
        #     contributor_obj = ContributorList.objects.get()


class ContributorListQuerySet(models.QuerySet):
    def permission(self, permission_level):
        return self.filter(Q(permission_level=permission_level) | Q(is_owner=True))

    def for_write_up(self, write_up_uuid):
        return self.select_related('write_up').get(write_up__uuid=write_up_uuid)


class ContributorListManager(models.Manager):
    def get_queryset(self):
        return ContributorListQuerySet(self.model, using=self._db)

    def get_contributor_with_permission_for_writeup(self, write_up_uuid, permission_level):
        return self.get_queryset().permission(permission_level).for_write_up(write_up_uuid)


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
                                                     model='extendeduser')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                     related_name='write_up_contributors')
    object_id = models.PositiveIntegerField()
    contributor = GenericForeignKey('content_type', 'object_id')
    is_owner = models.BooleanField(default=False)
    share_XP = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    permissions = models.ManyToManyField('essential.Permission')
    write_up = models.ForeignKey(WriteUp, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = ContributorListManager()

    class Meta:
        unique_together = ("write_up", "object_id", "content_type")

    def __unicode__(self):
        return "'%s' of '%s'" % (self.contributor, self.write_up)


class BaseDesign(models.Model):
    """
    Directly patched to Revision History Model.
    Anything that is saved to this model is revised in a separate model.
    For revisions - Save using method 'save_with_rev'
    """

    title = models.CharField(max_length=250, null=True, blank=True)
    text = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def save_with_rev(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # TODO: send user
        RevisionHistory.objects.create(user=user, parent=self, title=self.title, text=self.text)
        super(BaseDesign, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)


class MagazineArticles(models.Model):
    """
    It is the intermediary table for Write up type 'Magazine' and its units 'article'.
    A Magazine can have multiple articles. An article can wither be independent that is
    to have an explicit relation with Writeup model or have implicit relation with base
    design which depicts that the article solely belongs to the Magazine.
    """
    magazine = models.ForeignKey(WriteUp)
    LIMIT = models.Q(app_label='write_up',
                     model='writeup') | models.Q(app_label='write_up',
                                                 model='basedesign')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                     related_name='magazine_units')
    object_id = models.PositiveIntegerField()
    article = GenericForeignKey('content_type', 'object_id')


class BookChapter(models.Model):
    """ Intermediary table for relation between Write up type 'Book' and chapter (Base Design). """
    write_up = models.ForeignKey(WriteUp)
    chapter = models.OneToOneField(BaseDesign)

    def __unicode__(self):
        return self.write_up


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


class GroupWriting(models.Model):  # TODO: Celery task to unlock objects, calculate X & Y min max
    """
    For Group writing events. Only for users and not Publications.
    Sequentially users can add on to a story/article.
    Concurrent development is to be avoided as it violates the concept (until stories can be branched).
    No Revision History
    Locking mechanism to avoid concurrent development: While the user is actively extending the
    article, every 'X' min. make an api call to keep the object locked. After 'Y' min ask the user to
    fill captcha to rest 'Y' timer. If either X or Y exceeds, unlock the table back. and make the current session void.

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
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.article


class RevisionHistory(models.Model):  # TODO: handle same session saves in same entry
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
