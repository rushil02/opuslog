from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import View

from admin_custom.custom_errors import PermissionDenied
from write_up.forms import WriteUpForm, AddContributorForm


def check_user(request):
    user = request.user
    if user.is_active:
        if user.is_superuser:
            return redirect(reverse('admin_custom:home'))
        elif user.is_staff:
            return redirect(reverse('staff:home'))
        else:
            return user_acc(request)
    else:
        logout(request)


class MainView(View):
    login_form_class = AuthenticationForm
    signup_form_class = UserCreationForm
    template_name = 'user/main.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return check_user(request)
        login_form = self.login_form_class()
        signup_form = self.signup_form_class()
        context = {
            'login_form': login_form,
            'signup_form': signup_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.login_form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class RegisteredUser(MainView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Logged in")


def user_acc(request):
    return HttpResponse("Logged In")


@login_required
def create_edit_writeup(request, writeup_uuid=None):
    user = request.user
    template_name = ""
    success_redirect_url = ""

    if writeup_uuid:
        try:
            write_up = user.get_user_writeup_with_permission(writeup_uuid, 'E')
        except Exception:
            raise SuspiciousOperation()
        else:
            form = WriteUpForm(request.POST or None, instance=write_up)
    else:
        form = WriteUpForm(request.POST or None)

    context = {
        "form": form
    }

    if request.POST:
        if form.is_valid():
            write_up = form.save(commit=False)
            write_up.save(owner=user)
            return redirect(success_redirect_url)
        else:
            return render(request, template_name, context)
    else:
        return render(request, template_name, context)


@login_required
def add_write_up_contributor(request, write_up_uuid):
    user = request.user
    form = AddContributorForm(request.POST or None)
    template_name = ""
    success_redirect_url = ""

    context = {
        "form": form
    }

    if request.POST:
        if form.is_valid():

            contributor_username = form.cleaned_data['username']
            permission_level = form.cleaned_data['permission_level']
            share_XP = form.cleaned_data['share_XP']
            share_money = form.cleaned_data['share_money']

            if write_up_uuid and contributor_username and permission_level:
                try:
                    write_up = user.get_user_writeup_with_permission(write_up_uuid, 'E')
                    contributor = get_user_model().objects.get(username=contributor_username)
                except (PermissionDenied, ObjectDoesNotExist):
                    raise SuspiciousOperation()
                else:
                    # FIXME: send notification to contributor whether he likes to accept or not
                    write_up.add_contributor(contributor, permission_level, share_XP, share_money)
                    return redirect(success_redirect_url)
        else:
            return render(request, template_name, context)
    else:
        return render(request, template_name, context)
