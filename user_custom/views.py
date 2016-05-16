from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import View


# Create your views here.


class MainView(View):
    login_form_class = AuthenticationForm
    signup_form_class = UserCreationForm
    template_name = 'user/main.html'

    def get(self, request, *args, **kwargs):
        login_form = self.login_form_class()
        signup_form = self.signup_form_class()
        context = {
            'login_form': login_form,
            'signup_form': signup_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
