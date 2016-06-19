from django.core.exceptions import PermissionDenied

from publication.models import ContributorList


class UserPublicationPermissionMixin(object):
    """
    Checks for set permissions in a class based View before accessing
    the dispatch.
    """

    permissions = {}
    contributor = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            raise PermissionDenied

        contributor = ContributorList.objects.filter(
            contributor=request.user, publication=request.user.publication_identity
        )

        if self.permissions.get(str(request.method.lower())):
            for permission in self.permissions.get(str(request.method.lower())):
                contributor = contributor.filter(permissions__code_name=permission)
        else:
            raise PermissionDenied

        if not contributor:
            raise PermissionDenied

        self.contributor = contributor

        return super(UserPublicationPermissionMixin, self).dispatch(request, *args, **kwargs)
