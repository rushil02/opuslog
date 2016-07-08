from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseForbidden

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


class PublicationWriteUpPermissionMixin(object):
    group_contributor = None

    def post_permission_check(self, request, *args, **kwargs):
        method_permission_list = self.permissions.get(request.method.lower(), None)
        if method_permission_list:
            write_up = self.contributor.write_up
            if self.contributor.is_owner:
                group = write_up.group
            else:
                group = self.get_actor().group.get(contributed_group=True)
            try:
                self.group_contributor = group.get_contributor_with_perm(method_permission_list,
                                                                         self.get_actor_for_activity())
                # fixme: add get actor for activity
            except:
                return HttpResponseForbidden()
        super(PublicationWriteUpPermissionMixin, self).post_permission_check(request, *args, **kwargs)
