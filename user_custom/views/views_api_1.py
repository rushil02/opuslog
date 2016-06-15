from engagement.views import CommentFirstLevelView, CommentNestedView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class GetActor(object):
    """ For Method inherited by every User API class."""

    def get_actor(self):
        return self.request.user


class UserThreads(GetActor, ThreadView):
    """ Implements ThreadView for User entity. """

    def get_queryset(self):
        return Thread.objects.filter(threadmembers__user=self.request.user).select_related('created_by')


class AddDeleteMemberToThread(AddDeleteMemberView):
    """ Implements AddDeleteMemberView for User entity. """
    pass


class MessageOfThread(MessageView):
    """ Implements MessageView for User entity. """
    pass


class UserCommentFirstLevel(GetActor, CommentFirstLevelView):
    """ Implements UserView for posting/fetching first level comments. """
    pass


class UserCommentNested(GetActor, CommentNestedView):
    """ Implements UserView for posting/fetching nested comments. """
    pass
