import re

from django import forms
from .models import Program, Session

char_set = re.compile(r'^[\w]{5}$')


class SessionSelectForm(forms.Form):
    session = forms.CharField(max_length=5, label="Enter Session Code")

    def clean_session(self):
        data = self.cleaned_data['session']
        if len(data) != 5:
            raise forms.ValidationError("Session code should be 5 characters long")
        if char_set.fullmatch(data) is None:
            raise forms.ValidationError("Session code only be alphanumeric")

        try:
            data = Session.objects.get(session__exact=data)
        except (Session.DoesNotExist, Session.MultipleObjectsReturned):
            raise forms.ValidationError("Unknown Session code")

        return data


class ProgramSelectForm(forms.Form):
    program = forms.ModelChoiceField(Program.objects.filter(archived=False))
