from django import forms


class NameForm(forms.Form):
    value = forms.CharField(label='anything', max_length=100)