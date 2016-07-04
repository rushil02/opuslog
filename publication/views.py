from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from publication.permissions import UserPublicationPermissionMixin
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class GetActor(object):
    """ For Method inherited by every Publication API class."""

    actor = None

    def get_actor(self):
        if not self.actor:
            self.actor = self.request.user.publication_identity
        return self.actor

    def get_actor_handler(self):
        return self.get_actor().handler

    def get_actor_for_activity(self):
        obb = self.get_actor().contributorlist_set.get(contributor=self.request.user)
        print obb
        return obb


class PublicationThreads(GetActor, UserPublicationPermissionMixin, ThreadView):
    """ Implements ThreadView for Publication entity. """

    # permissions = ['access_threads']
    permissions = {'get': ['read_threads'], 'post': ['create_threads'], 'patch': ['update_threads']}
    permission_classes = []

    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmember__publication=self.get_actor()).prefetch_related('created_by')
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())


class AddDeleteMemberToThread(GetActor, UserPublicationPermissionMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """

    permissions = {'post': ['create_ThreadMember'], 'delete': ['delete_ThreadMember']}
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())


class MessageOfThread(GetActor, UserPublicationPermissionMixin, MessageView):
    """ Implements MessageView for Publication entity. """

    permissions = {'get': ['read_messages'], 'post': ['create_messages'], }
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())

    def set_user(self):
        return self.request.user


def publication_page(request, publication_handler):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's {%s} home page" % publication_handler)


class PublicationCommentFirstLevel(GetActor, CommentFirstLevelView):
    """ Implements PublicationView for posting/fetching first level comments. """
    pass


class PublicationCommentNested(GetActor, CommentNestedView):
    """ Implements PublicationView for posting/fetching nested comments. """
    pass


class PublicationCommentDelete(GetActor, DeleteCommentView):
    """ Implements PublicationView for deleting any comment. """
    pass


class PublicationVoteWriteup(GetActor, VoteWriteupView):
    """ Implements PublicationView for up/down voting a writeup, or deleting so """
    pass


class PublicationSubscriber(GetActor, SubscriberView):
    """ Implements PublicationView for Subscribing a publication or user """
    pass


class PublicationVoteComment(GetActor, VoteCommentView):
    """ Implements PublicationView for up/down voting a comment, or deleting so """
    pass
