from django.core.exceptions import SuspiciousOperation

from messaging_system.models import Thread
from messaging_system.views import ThreadView
from publication.models import Publication


class FetchPublication(object):  # Seems i wont be using it, makes 2 extra queries acc. to DjDT

    def get_publication(self):
        return Publication.objects.get(contributorlist__contributor=self.request.user, contributorlist__current=True)


class PublicationThreads(ThreadView):
    def get_queryset(self):
        try:
            return Thread.objects.filter(threadmembers__publication__contributorlist__contributor=self.request.user,
                                         threadmembers__publication__contributorlist__current=True)
        except Exception as e:
            raise SuspiciousOperation(e.message)

    def get_entity(self):  # FIXME: how the fuck is this supposed to happen?
        return self.request.user.contributed_publications.filter(current=True).publication.get()
