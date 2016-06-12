from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from messaging_system.models import Thread
from messaging_system.views import ThreadView, AddDeleteMemberView, MessageView
from publication.models import Publication


class PublicationThreads(ThreadView):
    """ Implements ThreadView for Publication entity. """

    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmembers__publication__contributorlist__contributor=self.request.user,
                                         threadmembers__publication__contributorlist__current=True)
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_entity(self):
        return get_object_or_404(Publication, contributorlist__contributor=self.request.user,
                                 contributorlist__current=True)


class AddDeleteMemberToThread(AddDeleteMemberView):
    """ Implements AddDeleteMemberView for Publication entity. """
    pass


class MessageOfThread(MessageView):
    """ Implements MessageView for Publication entity. """
    pass


def publication_page(request):
    # TODO: redirect to this page when requested for a publication's detail page
    return HttpResponse("You reached on some other publication's home page")
