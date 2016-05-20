from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Engagement(models.Model):
    """
    Everything extending this acts as a log
    actor -> can be either a user or publication (via contributor list)
    """

    LIMIT = models.Q(app_label='publication',
                     model='contributorlist') | models.Q(app_label='auth',
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

    vote_type = models.BooleanField(default=True)
    write_up = models.ForeignKey('write_up.WriteUpCollection', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("content_type", "object_id",
                           "write_up")  # FIXME :PROBLEM unique together will not work with new Engagement model scheme


class Comment(Engagement):  # TODO: user-tag and reply based notification
    """
    Comments can not be deleted or edited but can be replied on (1 LEVEL).
    Deleting a comment removes the username from display
    users can be tagged using the '@' key-letter
    """

    write_up = models.ForeignKey('write_up.WriteUpCollection', on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False, null=False)
    reply_to = models.ForeignKey("self", null=True)
    delete_request = models.BooleanField(default=False)


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
                      model='publication') | models.Q(app_label='auth',
                                                      model='user')
    content_type_2 = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=LIMIT2,
                                       related_name='subscribed')
    object_id_2 = models.PositiveIntegerField()
    subscribed = GenericForeignKey('content_type_2', 'object_id_2')

    class Meta:
        unique_together = ("content_type", "object_id", "content_type_2", "object_id_2",)
