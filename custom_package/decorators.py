from functools import wraps

from django.core.exceptions import SuspiciousOperation


def has_write_up_perm(acc_perm_code=None, collection_type=None):
    def _has_write_up_perm(view_func):
        def _decorator(request, *args, **kwargs):
            try:
                uuid = kwargs.get('write_up_uuid')
                contributor = request.user.contribution.get_contributor_for_writeup_with_perm(
                    write_up_uuid=uuid, acc_perm_code=acc_perm_code, collection_type=collection_type
                )
            except Exception as e:
                raise SuspiciousOperation(e.message)
            else:
                kwargs.update({'contributor': contributor})
            return view_func(request, *args, **kwargs)

        return wraps(view_func)(_decorator)

    return _has_write_up_perm


def has_publication_perm(acc_perm_code=None):
    def _has_publication_perm(view_func):
        def _decorator(request, *args, **kwargs):
            try:
                contributor = request.user.contributed_publications.get_contributor_for_publication_with_perm(
                    publication=request.user.publication_identity, acc_perm_code=acc_perm_code
                )
            except Exception as e:
                raise SuspiciousOperation(e.message)
            else:
                kwargs.update({'publication_contributor': contributor})
            return view_func(request, *args, **kwargs)

        return wraps(view_func)(_decorator)

    return _has_publication_perm
