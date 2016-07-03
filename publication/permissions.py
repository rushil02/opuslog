from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect

from admin_custom.models import ActivityLog
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

        try:
            contributor = ContributorList.objects.filter(
                contributor=request.user, publication=request.user.publication_identity
            )
            if not contributor:
                raise AssertionError
        except AssertionError:
            return redirect(request.get_full_path()[4:])
        except Exception as e:
            ActivityLog.objects.create_log(
                request=request, level='C', message=str(e.message),
                act_type="Error in getting contributor object of Publication",
                arguments={'args': args, 'kwargs': kwargs}, actor=user,
                view='UserPublicationPermissionMixin'
            )
            return HttpResponseBadRequest()

        if self.permissions.get(str(request.method.lower())):
            for permission in self.permissions.get(str(request.method.lower())):
                contributor = contributor.filter(permissions__code_name=permission)
        else:
            raise PermissionDenied

        if not contributor:
            raise PermissionDenied

        self.contributor = contributor

        return super(UserPublicationPermissionMixin, self).dispatch(request, *args, **kwargs)
