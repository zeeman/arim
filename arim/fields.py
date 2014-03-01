import re
from django import forms


mac_pattern = re.compile("^[0-9a-f]{12}$")


class MacAddrFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MacAddrFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(MacAddrFormField, self).clean(value)

        value = value.lower().replace(':', '').replace('-', '')
        if mac_pattern.match(value) is None:
            raise forms.ValidationError('Invalid MAC address')
        value = reduce(lambda x,y: x + ':' + y,
                       (value[i:i+2] for i in xrange(0, 12, 2)))

        return value
