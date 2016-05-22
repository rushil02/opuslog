from __future__ import unicode_literals

import uuid
import os
import time

from django.contrib.auth.models import User
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


class WriteUpCollection(models.Model):
    """
    A Write Up can belong to a user, a publication or both.  # FIXME
    Therefore this table acts as a complete index of a library.

    Multiple ownership of a write up can be but should not be dealt here. This defies
    the purpose of contributors and creates a confusion regarding the meaning of this table.

    A user can push a writeup to its own publication, but not to a contributed publication/write_up.

    Collection will be composed of units. It can be a book or Magazine. By default for every user
    there will be a write up extending to a collection  marked as 'Independent'.
    user ->  holds the info who created the writeup
    up_votes, down_votes, comments -> counters to avoid aggregate querying
    """

    # FIXME: add generic foreign key to user and publication_contributorlist
    user = models.ForeignKey(User, null=True)
    publication = models.ForeignKey('publication.Publication',
                                    null=True)
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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.validate():
            raise AssertionError
        super(WriteUpCollection, self).save(*args, **kwargs)

    def validate(self):
        if self.user and self.publication:
            if self.publication == Publication.objects.get(creator=self.user):
                return True
            return False
        elif self.user or self.publication:
            return True
        return False


class ContributorList(models.Model):
    """ It holds the ...
    List of Contributor for each write up """

    contributor = models.ForeignKey(User, related_name='write_up_contributors')
    share_XP = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    share_money = models.DecimalField(default=0, max_digits=8, decimal_places=5)
    write_up = models.ForeignKey(WriteUpCollection, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("write_up", "contributor")

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
        user = kwargs.pop('user', None)  # TODO: send post save signal with user custom signal
        super(BaseDesign, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)


class Unit(models.Model):
    """
    Unit acts as an intermediary table between write up collection and base design.
    That is, it stores all written matter against every collection.
    text -> is a foreign key since one base design can belong to multiple write ups.
            Eg. in case when an article belongs to multiple magazines.
    Therefore, this is a intermediary log for all relations between Base design and Collection
    """

    write_up = models.ForeignKey(WriteUpCollection)
    text = models.ForeignKey(BaseDesign)

    def __unicode__(self):
        return self.write_up


class LiveWriting(models.Model):
    """
    No Revision History
    Save to same BaseDesign object repetitively
    closed group -> if only restricted group of people should be part of the event, then True
    """

    write_up = models.OneToOneField(WriteUpCollection)
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

    write_up = models.OneToOneField(WriteUpCollection)
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


class RevisionHistory(models.Model):
    """ Stores textual revision history for BaseDesign model"""

    parent = models.ForeignKey(BaseDesign)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=250, null=True, blank=True)
    text = models.TextField()
    revision_num = models.PositiveSmallIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "'%s', revision: '%s'" % (self.parent, self.revision_num)
