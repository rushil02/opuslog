from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory

from write_up.models import WriteUp, BaseDesign, CollectionUnit


class CreateWriteUpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups')
        super(CreateWriteUpForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ModelChoiceField(queryset=groups)
        if groups.count() == 1:
            self.fields['group'].initial = groups[0]
            self.fields['group'].widget = forms.HiddenInput()

    class Meta:
        model = WriteUp
        fields = ['title', 'description', 'cover', 'collection_type', 'group']


class EditWriteUpForm(forms.ModelForm):
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


class BaseDesignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        write_up = kwargs.pop('write_up', None)
        article_unit = kwargs.pop('article_unit', None)
        super(BaseDesignForm, self).__init__(*args, **kwargs)
        if write_up.collection_type == 'I':
            self.fields['title'].initial = write_up.title
        elif write_up.collection_type == 'M':
            self.fields['title'].initial = article_unit.title

    title = forms.CharField(max_length=250)
    revision_history_title = forms.CharField(max_length=250, required=False)

    class Meta:
        model = BaseDesign
        fields = ['text']

    def clean_revision_history_title(self):
        if 'save_with_revision' in self.data:
            if self.cleaned_data['revision_history_title'] in ["", None]:
                raise ValidationError("This field is required.")
            return self.cleaned_data['revision_history_title']


class CollectionUnitForm(forms.ModelForm):
    title = forms.CharField(max_length=250)

    class Meta:
        model = CollectionUnit
        fields = ['sort_id']


EditPermissionFormSet = formset_factory(EditPermissionForm)
CollectionUnitFormSet = inlineformset_factory(WriteUp, CollectionUnit, form=CollectionUnitForm)
