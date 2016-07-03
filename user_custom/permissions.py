from django.shortcuts import redirect


class CheckUserMixin(object):
    """
    Checks for set permissions in a class based View before accessing
    the dispatch.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.publication_identity:
            return redirect('/pub' + request.get_full_path())
        return super(CheckUserMixin, self).dispatch(request, *args, **kwargs)
