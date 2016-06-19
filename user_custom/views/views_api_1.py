from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from engagement.views import CommentFirstLevelView, CommentNestedView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class GetActor(object):
    """ For Method inherited by every User API class."""

    def get_actor(self):
        return self.request.user


class UserThreads(GetActor, ThreadView):
    """ Implements ThreadView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(threadmember__user=self.request.user).select_related('created_by')

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.request.user)


class AddDeleteMemberToThread(GetActor, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())


class MessageOfThread(GetActor, MessageView):
    """ Implements MessageView for User entity. """

    permission_classes = [IsAuthenticated]

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__user=self.get_actor())

    def set_user(self):
        return None


class UserCommentFirstLevel(GetActor, CommentFirstLevelView):
    """ Implements UserView for posting/fetching first level comments. """
    pass


class UserCommentNested(GetActor, CommentNestedView):
    """ Implements UserView for posting/fetching nested comments. """
    pass
