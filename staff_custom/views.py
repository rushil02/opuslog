from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponse


@user_passes_test(lambda u: u.is_staff)
def home(request):
    return HttpResponse("STAFF PANEL")
