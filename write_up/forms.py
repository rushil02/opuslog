from django import forms
from django.forms.formsets import formset_factory

from write_up.models import WriteUp, BaseDesign


class CreateWriteUpForm(forms.ModelForm):
    class Meta:
        model = WriteUp
        fields = ['title', 'description', 'cover', 'collection_type']


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


# class BookChapterForm(forms.ModelForm):
#     class Meta:
#         model = BookChapter
#         fields = ['title']


class IndependentArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        write_up = kwargs.pop('write_up')
        super(IndependentArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = write_up.title

    title = forms.CharField(max_length=250)

    class Meta:
        model = BaseDesign
        fields = ['text']


EditPermissionFormSet = formset_factory(EditPermissionForm)
