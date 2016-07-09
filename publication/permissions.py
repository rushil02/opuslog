from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseForbidden

from admin_custom.models import ActivityLog
from publication.models import ContributorList


class PublicationContributorPermissionMixin(object):
    """
    Checks for set permissions in a class based View before accessing
    the dispatch.
    """

    permissions = {}
    contributor = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pub_handler = self.kwargs.get('pub_handler')
        permission_list = self.permissions.get(str(request.method.lower()), None)

        if not user.is_authenticated():
            raise PermissionDenied

        # if permission_list:
        try:
            self.contributor = ContributorList.objects.get_contributor_for_publication_with_perm(
                pub_handler, permission_list, user
            )
        except Exception as e:
            ActivityLog.objects.create_log(
                request=request, level='C', message=str(e.message),
                act_type="Error in getting contributor object of Publication",
                arguments={'args': args, 'kwargs': kwargs}, actor=user,
                view='PublicationContributorPermissionMixin'
            )
            return HttpResponseForbidden()
        return super(PublicationContributorPermissionMixin, self).dispatch(request, *args, **kwargs)


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
