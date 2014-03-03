from django import forms

from .fields import MacAddrFormField


class DeviceForm(forms.Form):
    description = forms.CharField(required=True, max_length=255)
    mac = MacAddrFormField(required=True)
    id = forms.IntegerField(required=False)


class TermsForm(forms.Form):
    agree1 = forms.BooleanField(required=True)
    agree2 = forms.BooleanField(required=True)