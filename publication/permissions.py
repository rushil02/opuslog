from django.http.response import HttpResponseForbidden

from admin_custom.models import ActivityLog
from essential.models import GroupContributor, WriteUpContributor
from publication.models import ContributorList


class PublicationContributorPermissionMixin(object):
    """
    Checks for set permissions in a class based View before accessing
    the dispatch.
    """

    publication_permissions = {}
    publication_contributor = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pub_handler = self.kwargs.get('pub_handler')
        permission_list = self.publication_permissions.get(str(request.method.lower()), [])

        try:
            self.publication_contributor = ContributorList.objects.get_contributor_for_publication_with_perm(
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


class PublicationContributorGroupPermissionMixin(object):
    group_contributor = None
    write_up_object_contributor = None
    group_permissions = {}

    def post_permission_check(self, request, *args, **kwargs):
        method_permission_list = self.group_permissions.get(request.method.lower(), [])
        if method_permission_list:
            group = self.contributor.group
            try:
                self.group_contributor = GroupContributor.objects.get_contributor_for_group_with_perm(group=group,
                                                                                                      permission_list=method_permission_list,
                                                                                                      contributor=self.get_actor_for_activity())
            except:
                write_up = self.contributor.write_up
                try:
                    self.write_up_object_contributor = WriteUpContributor.objects.get_contributor_for_write_up_with_perm(
                        write_up=write_up,
                        permission_list=method_permission_list,
                        contributor=self.get_actor_for_activity())
                except:
                    return HttpResponseForbidden()
        return super(PublicationContributorGroupPermissionMixin, self).post_permission_check(request, *args, **kwargs)
