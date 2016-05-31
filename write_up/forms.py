from django import forms
from write_up.models import WriteUp


class WriteUpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('initial'):
            self.Meta.fields.append('collection_type')
        super(WriteUpForm, self).__init__(*args, **kwargs)

    class Meta:
        model = WriteUp
        fields = ['title', 'description', 'cover']
