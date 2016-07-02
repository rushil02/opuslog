from __future__ import unicode_literals
import os
import time
from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from engagement.tasks import process_comment


def get_file_path(instance, filename):
    path = 'Comments/' + time.strftime('/%Y/%m/%d/')
    ext = filename.split('.')[-1]
    filename = "file-%s.%s" % (int(time.mktime(datetime.now().timetuple())), ext)
    return os.path.join(path, filename)


class Engagement(models.Model):
    """
    Everything extending this acts as a log
    actor -> can be either a user or publication
    """

    LIMIT = models.Q(app_label='publication',
                     model='publication') | models.Q(app_label='user_custom',
                                                     model='user')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT)
    object_id = models.PositiveIntegerField()
    actor = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class VoteWriteUp(Engagement):
    """
    Log for Up Votes on Write ups
    vote_type -> False:DownVote, True:UpVote
    """

    vote_type = models.NullBooleanField(default=True)
    write_up = models.ForeignKey('write_up.WriteUp', on_delete=models.CASCADE)
    validation = models.NullBooleanField(null=True, default=None)  # TODO: discuss feasibility

    class Meta:
        unique_together = ("content_type", "object_id", "write_up")


class Comment(Engagement):
    """
    Comments can not be deleted or edited but can be replied on (1 LEVEL).
    Deleting a comment changes the content for display as -
    "Comment deleted by user"
    users can be tagged using the '@' key-letter
    """

    write_up = models.ForeignKey('write_up.WriteUp', on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    up_votes = models.PositiveIntegerField(default=0)
    down_votes = models.PositiveIntegerField(default=0)
    replies_num = models.PositiveSmallIntegerField(default=0)
    reply_to = models.ForeignKey("self", null=True, blank=True)
    delete_flag = models.BooleanField(default=False)

    flagged_entity = GenericRelation('moderator.FlaggedEntity', related_query_name='comment')

    def process_comment_async(self):
        process_comment.delay(self.id)


class VoteComment(Engagement):
    """
    Log for likes on Comments
    vote_type -> False:DownVote, True:UpVote
    """

    vote_type = models.BooleanField(default=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("content_type", "object_id", "comment")


class Subscriber(Engagement):
    """
    Log for Subscribers

    **User can Subscribe User
    User can Subscribe Publisher
    Publisher can Subscribe Publisher
    Publisher can Subscribe User**
    """
    LIMIT2 = models.Q(app_label='publication',
                      model='publication') | models.Q(app_label='user_custom',
                                                      model='user')
    content_type_2 = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT2,
                                       related_name='subscribed')
    object_id_2 = models.PositiveIntegerField()
    subscribed = GenericForeignKey('content_type_2', 'object_id_2')
    unsubscribe_flag = models.BooleanField(default=False)

    class Meta:
        unique_together = ("content_type", "object_id", "content_type_2", "object_id_2",)
