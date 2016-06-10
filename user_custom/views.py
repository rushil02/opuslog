from allauth.account.views import LoginView, login
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import View

from admin_custom.custom_errors import PermissionDenied
from admin_custom.decorators import has_write_up_perm
from user_custom.forms import CustomLoginForm, CustomSignupForm
from write_up.forms import AddContributorForm, EditPermissionFormSet, IndependentArticleForm, EditWriteUpForm
from write_up.views import CreateWriteUpView


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
    login_form_class = CustomLoginForm
    signup_form_class = CustomSignupForm
    template_name = 'user/main.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return check_user(request)
        login_form = self.login_form_class(captcha_flag=False)
        signup_form = self.signup_form_class()
        context = {
            'login_form': login_form,
            'signup_form': signup_form,
        }
        return render(request, self.template_name, context)


@method_decorator(require_POST, name='dispatch')
class CustomLoginView(LoginView):
    def get_form_class(self):
        return CustomLoginForm

    def get_form_kwargs(self):
        kwargs = super(CustomLoginView, self).get_form_kwargs()
        kwargs.update({'captcha_flag': False})
        return kwargs

    def form_invalid(self, form):
        return login(self.request, self.get_context_data(form=form))


class RegisteredUser(MainView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Logged in")


def user_acc(request):
    return HttpResponse("Logged In")


@has_write_up_perm('CAN_EDIT', collection_type='I')
def edit_independent_article(request, *args, **kwargs):
    contributor = kwargs.get('contributor')
    write_up = contributor.write_up
    article_unit = write_up.unit
    article_base_design = article_unit.text
    success_redirect_url = ""
    template_name = "write_up/form_template.html"

    form = IndependentArticleForm(request.POST or None, instance=article_base_design, write_up=write_up)

    context = {
        "form": form
    }

    if request.POST:
        if form.is_valid():
            if form.cleaned_data['title'] != write_up.title:
                write_up.title = form.cleaned_data['title']
                write_up.save()
            form.save()
            return redirect(success_redirect_url)
    return render(request, template_name, context)


# @has_write_up_perm(acc_perm_code='CAN_EDIT', collection_type='B')
# def create_chapter_view(request, *args, **kwargs):
#     contributor = kwargs.get('contributor')
#     write_up = contributor.write_up
#     template_name = ""
#     success_redirect_url = ""
#
#     form = BookChapterForm(request.POST or None)
#     context = {
#         "form": form
#     }
#
#     if request.POST:
#         if form.is_valid():
#             book_chapter = form.save(commit=False)
#             base_design = BaseDesign.objects.create()
#             book_chapter.book = write_up
#             book_chapter.chapter = base_design
#             book_chapter.relationship = 'I'
#             book_chapter.save()
#             return redirect(success_redirect_url)
#
#     chapters = write_up.get_all_chapters()
#     context.update({"chapters": chapters})
#     return render(request, template_name, context)


@login_required
@has_write_up_perm(acc_perm_code='CAN_EDIT')  # fixme: add perm code to permission table
def edit_write_up(request, *args, **kwargs):
    template_name = ""
    redirect_success_url = ""
    contributor = kwargs.get('contributor')
    try:
        write_up = contributor.write_up
    except ObjectDoesNotExist:
        raise SuspiciousOperation()
    else:
        form = EditWriteUpForm(request.POST or None, instance=write_up)
        context = {
            "form": form
        }
        if request.POST:
            if form.is_valid():
                form.save()
                return redirect(redirect_success_url)
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
                    # FIXME: send notification to contributor whether he likes to accept or not check if already exists
                    write_up.add_contributor(contributor, permission_level, share_XP, share_money)
                    return redirect(success_redirect_url)
        else:
            return render(request, template_name, context)
    else:
        return render(request, template_name, context)


@login_required
def edit_permission_view(request, write_up_uuid):  # FIXME: Change permission usage
    user = request.user
    template_name = ""
    success_redirect_url = ""

    if not write_up_uuid:
        raise SuspiciousOperation()
    try:
        write_up = user.get_user_writeup_with_permission(write_up_uuid, 'E')
    except PermissionDenied:
        raise SuspiciousOperation()
    else:
        contributors = write_up.get_all_contributors()
        formset = EditPermissionFormSet(request.POST or None,
                                        initial=[{'username': contributor, 'permission_level': contributor.permission_level}
                                                 for contributor in contributors])
        context = {
            "formset": formset
        }

        if request.POST:
            if formset.is_valid():
                for (contributor, form) in zip(contributors, formset):
                    remove = form.cleaned_data['remove']
                    if remove:
                        # FIXME: Remove the contributor
                        pass
                    elif contributor.permission_level != form.cleaned_data['permission_level']:
                        contributor.permission_level = form.cleaned_data['permission_level']
                        contributor.save()

                return redirect(success_redirect_url)
            else:
                return render(request, template_name, context)
        else:
            return render(request, template_name, context)


def alter_identity(request):  # TODO
    pass


@method_decorator(login_required, name='dispatch')
class CreateUserWriteUpView(CreateWriteUpView):
    def get_success_url(self):
        return super(CreateUserWriteUpView, self).get_success_url()

    def get_user(self):
        return self.request.user

    def get_publication_user(self):
        return None
