import abc

from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin

from django.views.generic.edit import BaseCreateView, BaseUpdateView

from write_up.forms import CreateWriteUpForm, EditWriteUpForm
from write_up.models import WriteUp


class UserPublicationMixin(object):
    @abc.abstractmethod
    def get_user(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_publication_user(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_success_url_prefix(self):
        raise NotImplementedError("Not Implemented Error")


class CreateWriteUpView(UserPublicationMixin, TemplateResponseMixin, BaseCreateView):
    form_class = CreateWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"

    def get_success_url(self):
        write_up = self.object
        url = write_up.get_handler_redirect_url()
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + url + str(write_up.uuid)

    def form_valid(self, form):
        user = self.get_user()
        self.object = form.save()
        write_up = self.object
        write_up.set_owner(user, publication_user=self.get_publication_user())
        write_up.create_write_up_handler(user=user)
        return HttpResponseRedirect(self.get_success_url())


class EditWriteUpView(UserPublicationMixin, TemplateResponseMixin, BaseUpdateView):
    form_class = EditWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"

    def get_object(self, queryset=None):
        contributor = self.kwargs.get('contributor')
        return contributor.write_up

    def get_success_url(self):
        write_up = self.object
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + "/edit_write_up/" + str(write_up.uuid)
