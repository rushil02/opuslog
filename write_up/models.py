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

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from publication.models import Publication


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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.validate():
            raise AssertionError
        super(WriteUp, self).save(*args, **kwargs)

    def validate(self):
        if self.user and self.publication:
            if self.publication == Publication.objects.get(creator=self.user):
                return True
            return False
        elif self.user or self.publication:
            return True
        return False


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
                     model='publication') | models.Q(app_label='auth',
                                                     model='user')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                     related_name='write_up_contributors')
    object_id = models.PositiveIntegerField()
    contributor = GenericForeignKey('content_type', 'object_id')
    is_owner = models.BooleanField(default=False)
    share_XP = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    LEVEL = (('E', 'Can edit'),  # TODO: Extend list of tags as required
             ('D', 'Can Delete'),
             ('S', 'Show in their list'),
             )
    permission_level = models.CharField(max_length=1, choices=LEVEL)
    write_up = models.ForeignKey(WriteUp, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

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


class Magazine(models.Model):
    magazine = models.ForeignKey(WriteUp)
    LIMIT = models.Q(app_label='write_up',
                     model='writeup') | models.Q(app_label='write_up',
                                                 model='basedesign')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT,
                                     related_name='magazine_units')
    object_id = models.PositiveIntegerField()
    units = GenericForeignKey('content_type', 'object_id')


# ***ALTERNATE MAGAZINE MODEL***

# class Magazine(models.Model):
#     magazine = models.ForeignKey(WriteUp)
#     shared_unit = models.ForeignKey(WriteUp, null=True)
#     implicit_unit = models.OneToOneField(BaseDesign, null=True)


class Book(models.Model):
    write_up = models.ForeignKey(WriteUp)
    text = models.OneToOneField(BaseDesign)

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
    closed_group_users = models.ManyToManyField(User)
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
    closed_group_users = models.ManyToManyField(User)
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
    writer = models.ForeignKey(User)
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
    user = models.ForeignKey(User)
    title = models.CharField(max_length=250, null=True, blank=True)
    text = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "'%s', revision at: '%s'" % (self.parent, self.update_time)
