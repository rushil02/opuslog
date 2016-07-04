from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, UpVoteWriteupView, \
    DownVoteWriteupView, RemoveVoteWriteupView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView
from user_custom.permissions import CheckUserMixin


class GetActor(object):
    """ For Method inherited by every User API class."""

    def get_actor(self):
        return self.request.user

    def get_actor_handler(self):
        return self.get_actor().username

    def get_actor_for_activity(self):
        return self.get_actor()


class UserThreads(CheckUserMixin, GetActor, ThreadView):
    """ Implements ThreadView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(threadmember__user=self.get_actor()).prefetch_related('created_by')

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class AddDeleteMemberToThread(CheckUserMixin, GetActor, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class MessageOfThread(CheckUserMixin, GetActor, MessageView):
    """ Implements MessageView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())

    def set_user(self):
        return None


class UserCommentFirstLevel(CheckUserMixin, GetActor, CommentFirstLevelView):
    """ Implements UserView for posting/fetching first level comments. """
    pass


class UserCommentNested(CheckUserMixin, GetActor, CommentNestedView):
    """ Implements UserView for posting/fetching nested comments. """
    pass


class UserCommentDelete(CheckUserMixin, GetActor, DeleteCommentView):
    """ Implements UserView for deleting any comment. """
    pass


class UserUpVoteWriteup(CheckUserMixin, GetActor, UpVoteWriteupView):
    """ Implements UserView for up voting a writeup """
    pass


class UserDownVoteWriteup(CheckUserMixin, GetActor, DownVoteWriteupView):
    """ Implements UserView for down voting a writeup """
    pass


class UserRemoveVoteWriteup(CheckUserMixin, GetActor, RemoveVoteWriteupView):
    """ Implements UserView for removing a vote on a writeup """
    pass
