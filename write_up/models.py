from __future__ import unicode_literals

import uuid
import os
import time

from django.contrib.auth.models import User
from django.db import models


# Image file rename
def get_file_path(instance, filename):
    if instance.collection_type == 'B':
        path = 'Covers/Book' + time.strftime('/%Y/%m/%d/')
    elif instance.collection_type == 'M':
        path = 'Covers/Magazine' + time.strftime('/%Y/%m/%d/')
    else:
        return False

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.write_up.uuid, ext)
    return os.path.join(path, filename)


class WriteUp(models.Model):
    shelf = models.ForeignKey(User, null=True)
    publication = models.ForeignKey('publication.Publication',
                                    null=True)  # TODO: Can single write up have multiple publications?
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if self.shelf and self.publication:
            return "'%s' & '%s'" % (self.shelf, self.publication)
        elif self.shelf:
            return self.shelf
        elif self.publication:
            return self.publication

    def save(self, *args, **kwargs):
        if not self.validate():
            raise AssertionError
        super(WriteUp, self).save(*args, **kwargs)

    def validate(self):
        if self.shelf or self.publication:
            return True
        return False


class ContributorList(models.Model):
    contributor = models.ForeignKey(User, related_name='write_up_contributors')
    share_XP = models.PositiveSmallIntegerField(default=0)
    share_money = models.PositiveSmallIntegerField(default=0)
    write_up = models.ForeignKey(WriteUp, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("write_up", "contributor")


class BaseDesign(models.Model):
    """ Revision History """
    text = models.TextField()

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        RevisionHistory.objects.create(parent=self, user=user, text=self.text)
        super(BaseDesign, self).save(*args, **kwargs)


class Collection(models.Model):
    write_up = models.OneToOneField(WriteUp)
    TYPE = (('B', 'Book'),
            ('M', 'Magazine'),
            )
    collection_type = models.CharField(max_length=1, choices=TYPE)
    description = models.TextField()
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)


class Article(models.Model):
    write_up = models.OneToOneField(WriteUp)
    magazine = models.ForeignKey(Collection, null=True)
    text = models.OneToOneField(BaseDesign)


class Chapter(models.Model):
    book = models.OneToOneField(Collection)
    text = models.OneToOneField(BaseDesign)


class LiveWriting(BaseDesign):
    """ No Revision History """
    write_up = models.OneToOneField(WriteUp)

    def save(self, *args, **kwargs):
        super(BaseDesign, self).save(*args, **kwargs)


class GroupWriting(BaseDesign):
    """ No Revision History """
    write_up = models.ForeignKey(WriteUp)
    sequence = models.PositiveSmallIntegerField()
    writer = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(BaseDesign, self).save(*args, **kwargs)


class RevisionHistory(models.Model):
    parent = models.ForeignKey(BaseDesign)
    user = models.ForeignKey(User)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
