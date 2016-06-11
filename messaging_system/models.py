from __future__ import unicode_literals
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models


class Thread(models.Model):
    """ Thread is created with group members. """

    subject = models.CharField(max_length=125)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.subject


class Message(models.Model):
    """ A private message from user to user """

    thread = models.ForeignKey(Thread)
    body = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.thread


class ThreadMembers(models.Model):
    """ Acts as intermediary table for Thread and User/Publication """

    thread = models.ForeignKey(Thread)

    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    removed = models.BooleanField(default=False)
    entity = GenericForeignKey('content_type', 'object_id')
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.entity.__unicode__()

    class Meta:
        unique_together = ('content_type', 'thread', 'object_id')