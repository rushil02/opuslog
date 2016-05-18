from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models


# class NotificationManager(models.Manager)

class Notification(models.Model):
    """
    Stores User related Notifications.
    Publication Notification are stored by referring settings for every user-publication relation
    and are generated for so

    details in JSON -> image <url> of actor (user/publication), publication or not, text to show, redirect url

    JSON format ->

    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = JSONField()
    notified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class RevisionHistory(models.Model):
    """ Stores textual revision history for BaseDesign model"""

    parent = models.ForeignKey('write_up.BaseDesign')
    user = models.ForeignKey(User)
    text = models.TextField()
    revision_num = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "'%s', revision: '%s'" % (self.parent, self.revision_num)


class GroupWritingLockHistory(models.Model):
    """ Stores request history made by a user to extend a Group writing Article """

    article = models.ForeignKey('write_up.GroupWriting')
    lock_request_user = models.ForeignKey(User)
    lock_start_time = models.DateTimeField()
    lock_last_request = models.DateTimeField()
    void = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "'%s' for '%s'" % (self.lock_request_user, self.article)
