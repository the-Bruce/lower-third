from django import forms


class SessionSelectForm(forms.Form):
    session = forms.CharField(max_length=5)

