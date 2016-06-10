import abc

from django.http.response import HttpResponseRedirect

from django.views.generic.edit import CreateView

from write_up.forms import CreateWriteUpForm
from write_up.models import WriteUp


class CreateWriteUpView(CreateView):
    form_class = CreateWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"

    def get_success_url(self):
        write_up = self.object
        url = write_up.get_handler_redirect_url()
        return url + str(write_up.uuid)

    def form_valid(self, form):
        user = self.get_user()
        self.object = form.save()
        write_up = self.object
        write_up.set_owner(user, publication_user=self.get_publication_user())
        write_up.create_write_up_handler(user=user)
        return HttpResponseRedirect(self.get_success_url())

    @abc.abstractmethod
    def get_user(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_publication_user(self):
        raise NotImplementedError("Not Implemented Error")
