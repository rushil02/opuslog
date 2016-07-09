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
