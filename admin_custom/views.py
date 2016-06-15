from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http.response import HttpResponse
from django.shortcuts import render


@user_passes_test(lambda u: u.is_superuser)
def home(request):
    return HttpResponse("ADMIN PANEL")


@user_passes_test(lambda u: u.is_superuser)
def staff_registration(request):
    sign_up_form = UserCreationForm(request.POST or None)
    if sign_up_form.is_valid() and request.POST:
        user = sign_up_form.save(commit=False)
        user.user_type = 'S'
        user.is_staff = True
        user.save()
        return HttpResponse("Staff user created")
    else:
        context = {
            "form": sign_up_form
        }
        return render(request, 'client_registration.html', context)
