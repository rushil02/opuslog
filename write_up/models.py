from __future__ import unicode_literals

import uuid
import os
import time

from django.contrib.auth.models import User
from django.db import models

from user_custom.models import Contributor


# Image file rename
def get_file_path(instance, filename):
    if instance.__class__.__name__ is 'Book':
        path = 'Covers/Book' + time.strftime('/%Y/%m/%d/')
    elif instance.__class__.__name__ is 'Magazine':
        path = 'Covers/Magazine' + time.strftime('/%Y/%m/%d/')
    else:
        return False

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.write_up.uuid, ext)
    return os.path.join(path, filename)


class WriteUp(models.Model):
    shelf = models.ForeignKey(User, null=True)
    publication = models.ForeignKey('publication.Publication', null=True)
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


class ContributorList(Contributor):
    write_up = models.ForeignKey(WriteUp, null=True)

    class Meta:
        unique_together = ("write_up", "contributor")


class BaseDesign(models.Model):
    text = models.TextField()


class Book(models.Model):
    write_up = models.OneToOneField(WriteUp)
    description = models.TextField()
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)


class Magazine(models.Model):
    write_up = models.OneToOneField(WriteUp)
    description = models.TextField()
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)


class Article(BaseDesign):
    write_up = models.OneToOneField(WriteUp)
    magazine = models.ForeignKey(Magazine, null=True)


class Chapter(BaseDesign):
    book = models.ForeignKey(Book)
