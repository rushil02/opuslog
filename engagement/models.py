from __future__ import unicode_literals
import re

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from essential.models import Notification


class Engagement(models.Model):
    """
    Everything extending this acts as a log
    actor -> can be either a user or publication
    publication_user -> stores the link to Contributor List model of publication app, in case the actor is publication
    """

    publication_user = models.ForeignKey('publication.ContributorList', null=True)
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

    vote_type = models.BooleanField(default=True)
    write_up = models.ForeignKey('write_up.WriteUp', on_delete=models.CASCADE)
    validation = models.NullBooleanField(null=True, default=None)  # TODO: discuss feasibility

    class Meta:
        unique_together = ("content_type", "object_id", "write_up")


class Comment(Engagement):
    """
    Comments can not be deleted or edited but can be replied on (1 LEVEL).
    Deleting a comment removes the username from display
    users can be tagged using the '@' key-letter
    """

    write_up = models.ForeignKey('write_up.WriteUp', on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False, null=False)
    up_votes = models.PositiveIntegerField(default=0)
    down_votes = models.PositiveIntegerField(default=0)
    reply_to = models.ForeignKey("self", null=True, blank=True)
    delete_request = models.BooleanField(default=False)

    flagged_entity = GenericRelation('moderator.FlaggedEntity', related_query_name='comment')

    def parse_text(self):
        username_list = [x.strip('@') for x in re.findall(r'\B@\w+', self.comment_text)]
        for username in username_list:
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                pass
            else:
                Notification.objects.notify(user=user, write_up=self.write_up, notification_type='CT')


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

    class Meta:
        unique_together = ("content_type", "object_id", "content_type_2", "object_id_2",)
