from django import forms

from .fields import MacAddrFormField


class DeviceForm(forms.Form):
    description = forms.CharField(required=True, max_length=255)
    mac = MacAddrFormField()
