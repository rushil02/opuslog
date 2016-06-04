from functools import wraps

from django.core.exceptions import SuspiciousOperation


def has_content_perm(acc_perm_code=None, perm_for=None):
    def _has_content_perm(view_func):
        def _decorator(request, *args, **kwargs):
            contributor = None
            try:
                if perm_for is 'W':
                    uuid = kwargs.get('write_up_uuid')
                    contributor = request.user.contribution.get_contributor_for_writeup_with_perm(
                        write_up_uuid=uuid, acc_perm_code=acc_perm_code
                    )
                elif perm_for is 'P':
                    uuid = kwargs.get('publication_uuid')
                    contributor = request.user.contributed_publications.get_contributor_for_publication_with_perm(
                        publication_uuid=uuid, acc_perm_code=acc_perm_code
                    )
            except Exception as e:
                raise SuspiciousOperation(e.message)
            else:
                if contributor:
                    kwargs.update({'contributor': contributor})
                else:
                    raise SuspiciousOperation("No contributor set")
            return view_func(request, *args, **kwargs)

        return wraps(view_func)(_decorator)

    return _has_content_perm
