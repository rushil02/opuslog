from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class AnonymousViewer(models.Model):
    write_up = models.ForeignKey('write_up.WriteUp')
    duration = models.PositiveSmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class RegisteredViewer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    write_up = models.ForeignKey('write_up.WriteUp')
    duration = models.PositiveSmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class GroupWritingLockHistory(models.Model):
    """ Stores lock request history made by a user to extend a Group writing Article """

    article = models.ForeignKey('write_up.GroupWriting')
    lock_request_user = models.ForeignKey(settings.AUTH_USER_MODEL)
    lock_start_time = models.DateTimeField()
    lock_last_request = models.DateTimeField()
    void = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "'%s' for '%s'" % (self.lock_request_user, self.article)
