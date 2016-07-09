from __future__ import unicode_literals
import time
import os
from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models


def get_file_path(instance, filename):
    path = 'MessageFiles/' + time.strftime('/%Y/%m/%d/')
    ext = filename.split('.')[-1]
    filename = "file-%s.%s" % (int(time.mktime(datetime.now().timetuple())), ext)
    return os.path.join(path, filename)


class Thread(models.Model):
    """ Thread is created with group members. """

    subject = models.CharField(max_length=125)
    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    created_by = GenericForeignKey('content_type', 'object_id')
    create_time = models.DateTimeField(auto_now_add=True)

    for_requests = GenericRelation('essential.Request', content_type_field='request_for_content_type',
                                   object_id_field='request_for_object_id',
                                   related_query_name='thread_for_request')

    class CustomMeta:
        permission_list = [
            {'name': 'Can create threads', 'code_name': 'create_threads', 'for': 'P',
             'help_text': 'Allow contributor to create threads'},
            {'name': 'Can update threads', 'code_name': 'update_threads', 'for': 'P',
             'help_text': 'Allow contributor to update subject of threads'},
            {'name': 'Can read threads', 'code_name': 'read_threads', 'for': 'P',
             'help_text': 'Allow contributor to read list of threads'},
            {'name': 'Can delete threads', 'code_name': 'delete_threads', 'for': 'P',
             'help_text': 'Allow contributor to delete threads'},
        ]

    def __unicode__(self):
        return self.subject


class Message(models.Model):
    """ A private message from user to user """

    thread = models.ForeignKey(Thread)
    body = models.TextField()
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    sender = models.ForeignKey('messaging_system.ThreadMember')
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class CustomMeta:
        permission_list = [
            {'name': 'Can create messages', 'code_name': 'create_messages', 'for': 'P',
             'help_text': 'Allow contributor to create messages'},
            {'name': 'Can update messages', 'code_name': 'update_messages', 'for': 'P',
             'help_text': 'Allow contributor to update subject of messages'},
            {'name': 'Can read messages', 'code_name': 'read_messages', 'for': 'P',
             'help_text': 'Allow contributor to read list of messages'},
            {'name': 'Can delete messages', 'code_name': 'delete_messages', 'for': 'P',
             'help_text': 'Allow contributor to delete messages'},
        ]

    def __unicode__(self):
        return self.thread.subject


class ThreadMemberManager(models.Manager):
    def get_thread_members_for_thread(self, thread_id):
        return self.get_queryset().filter(thread__id=thread_id).prefetch_related()

    def add_thread_member_request(self, **kwargs):
        request_log = kwargs.get('request_log')
        answer = kwargs.get('answer')
        if answer:
            self.get_queryset().create(thread=request_log.request_for, entity=request_log.request_to)

        return '/url/'  # TODO: view url on accept and reject


class ThreadMember(models.Model):
    """
    Acts as intermediary table for Thread and User/Publication
    Holds all the meta information for each user-thread relationship.

    meta_info -> holds info unique to each user, example -
        mute - independent to each contributor, therefore key is the
               pk of contributor, while in case odf user mute is the
               first key
    """

    thread = models.ForeignKey(Thread)

    LIMIT = models.Q(
        app_label='publication', model='publication'
    ) | models.Q(
        app_label='user_custom', model='user'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    removed = models.BooleanField(default=False)
    meta_info = JSONField(null=True, blank=True)
    archive = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    objects = ThreadMemberManager()

    class CustomMeta:
        permission_list = [
            {'name': 'Can create ThreadMember', 'code_name': 'create_ThreadMember', 'for': 'P',
             'help_text': 'Allow contributor to create Thread Members'},
            {'name': 'Can update ThreadMember', 'code_name': 'update_ThreadMember', 'for': 'P',
             'help_text': 'Allow contributor to update subject of Thread Members'},
            {'name': 'Can read ThreadMember', 'code_name': 'read_ThreadMember', 'for': 'P',
             'help_text': 'Allow contributor to read list of Thread Members'},
            {'name': 'Can delete ThreadMember', 'code_name': 'delete_ThreadMember', 'for': 'P',
             'help_text': 'Allow contributor to delete Thread Members'},
        ]

    def __unicode__(self):
        return self.entity.__unicode__()

    class Meta:
        unique_together = ('content_type', 'thread', 'object_id')
