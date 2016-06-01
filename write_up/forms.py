from django import forms

from write_up.models import WriteUp
from write_up.models import ContributorList


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
    permission_level = forms.ChoiceField(widget=forms.Select(), choices=ContributorList.LEVEL)
    share_XP = forms.DecimalField(100, 0, max_digits=4, decimal_places=2)
    share_money = forms.DecimalField(100, 0, max_digits=4, decimal_places=2)
