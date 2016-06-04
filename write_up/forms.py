from django import forms
from django.forms.formsets import formset_factory

from write_up.models import WriteUp


class WriteUpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('initial'):
            self.Meta.fields.append('collection_type')
        super(WriteUpForm, self).__init__(*args, **kwargs)

    class Meta:
        model = WriteUp
        fields = ['title', 'description', 'cover']


class AddContributorForm(forms.Form):
    username = forms.EmailField(max_length=128)
    permission_level = forms.ChoiceField(widget=forms.Select())  # FIXME: Add choices for permission
    share_XP = forms.DecimalField(100, 0, max_digits=4, decimal_places=2)
    share_money = forms.DecimalField(100, 0, max_digits=4, decimal_places=2)


class EditPermissionForm(forms.Form):
    permission_level = forms.ChoiceField(widget=forms.Select())  # FIXME: Add choices for permission
    remove = forms.BooleanField(required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'disabled', 'readonly': 'readonly'}))


EditPermissionFormSet = formset_factory(EditPermissionForm)
