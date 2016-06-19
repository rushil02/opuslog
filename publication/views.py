from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from publication.permissions import UserPublicationPermissionMixin
from engagement.views import CommentFirstLevelView, CommentNestedView
from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView


class GetActor(object):
    """ For Method inherited by every Publication API class."""

    def get_actor(self):
        obj = self.request.user.publication_identity
        if obj:
            return obj
        else:
            raise SuspiciousOperation("No object found")


class PublicationThreads(GetActor, UserPublicationPermissionMixin, ThreadView):
    """ Implements ThreadView for Publication entity. """

    permissions = ['canAccess.Thread']

    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmembers__publication=self.get_actor())
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_thread_query(self, thread_id):
        return get_object_or_404(Thread, id=thread_id,
                                 threadmembers__publication=self.request.user.publication_identity)


class AddDeleteMemberToThread(AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """
    pass


class MessageOfThread(MessageView):
    """ Implements MessageView for Publication entity. """
    pass


def publication_page(request, publication_handler):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's {%s} home page" % publication_handler)


class PublicationCommentFirstLevel(GetActor, CommentFirstLevelView):
    """ Implements PublicationView for posting/fetching first level comments. """
    pass


class PublicationCommentNested(GetActor, CommentNestedView):
    """ Implements PublicationView for posting/fetching nested comments. """
    pass
