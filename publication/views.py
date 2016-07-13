from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from custom_package.mixins import PublicationMixin
from publication.permissions import PublicationContributorPermissionMixin
from engagement.views import CommentFirstLevelView, CommentNestedView, DeleteCommentView, VoteWriteupView, \
    SubscriberView, VoteCommentView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class PublicationThreads(PublicationContributorPermissionMixin, PublicationMixin, ThreadView):
    """ Implements ThreadView for Publication entity. """

    permissions = {'get': ['read_threads'], 'post': ['create_threads'], 'patch': ['update_threads']}
    permission_classes = []

    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmember__publication=self.get_actor()).prefetch_related('created_by')
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())

    def notify_post(self, obj):
        self.notify_self(
            notification_type='NT', acted_on=obj,
        )


class AddDeleteMemberToThread(PublicationContributorPermissionMixin, PublicationMixin, AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """

    permissions = {'post': ['create_ThreadMember'], 'delete': ['delete_ThreadMember']}
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, publication=self.get_actor())


class MessageOfThread(PublicationContributorPermissionMixin, PublicationMixin, MessageView):
    """ Implements MessageView for Publication entity. """

    permissions = {'get': ['read_messages'], 'post': ['create_messages'], }
    permission_classes = []

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id, threadmember__publication=self.get_actor())


def publication_page(request, pub_handler):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's {%s} home page" % pub_handler)


class PublicationCommentFirstLevel(PublicationContributorPermissionMixin, PublicationMixin, CommentFirstLevelView):
    """ Implements PublicationView for posting/fetching first level comments. """
    pass


class PublicationCommentNested(PublicationContributorPermissionMixin, PublicationMixin, CommentNestedView):
    """ Implements PublicationView for posting/fetching nested comments. """
    pass


class PublicationCommentDelete(PublicationContributorPermissionMixin, PublicationMixin, DeleteCommentView):
    """ Implements PublicationView for deleting any comment. """
    pass


class PublicationVoteWriteup(PublicationContributorPermissionMixin, PublicationMixin, VoteWriteupView):
    """ Implements PublicationView for up/down voting a writeup, or deleting so """
    pass


class PublicationSubscriber(PublicationContributorPermissionMixin, PublicationMixin, SubscriberView):
    """ Implements PublicationView for Subscribing a publication or user """
    pass


class PublicationVoteComment(PublicationContributorPermissionMixin, PublicationMixin, VoteCommentView):
    """ Implements PublicationView for up/down voting a comment, or deleting so """
    pass
