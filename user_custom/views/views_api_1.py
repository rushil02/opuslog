from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from custom_package.mixins import UserMixin
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from essential.views import AcceptDenyRequest
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class UserThreads(UserMixin, ThreadView):
    """ Implements ThreadView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(threadmember__user=self.get_actor()).prefetch_related('created_by')

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class AddDeleteMemberToThread(UserMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, user=self.get_actor())


class MessageOfThread(UserMixin, MessageView):
    """ Implements MessageView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class UserCommentFirstLevel(UserMixin, CommentFirstLevelView):
    """ Implements UserView for posting/fetching first level comments. """
    pass


class UserCommentNested(UserMixin, CommentNestedView):
    """ Implements UserView for posting/fetching nested comments. """
    pass


class UserCommentDelete(UserMixin, DeleteCommentView):
    """ Implements UserView for deleting any comment. """
    pass


class UserVoteWriteup(UserMixin, VoteWriteupView):
    """ Implements UserView for up/down voting a writeup, or deleting so"""
    pass


class UserSubscriber(UserMixin, SubscriberView):
    """ Implements UserView for Subscribing a publication or user """
    pass


class UserVoteComment(UserMixin, VoteCommentView):
    """ Implements UserView for up/down voting a comment, or deleting so """
    pass


class UserRequest(UserMixin, AcceptDenyRequest):
    """"""
    pass
