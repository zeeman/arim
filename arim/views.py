import json
from django.http import HttpResponse
from django.shortcuts import render

from .forms import DeviceForm
from .utils import HttpResponse422


def create_system(**kwargs):
    pass


def update_system(**kwargs):
    pass


def get_devices():
    return [
        {'description': 'Test system', 'mac': '01:23:45:67:89:ab', 'id': 3},
        {'description': 'Test system 2', 'mac': '01:23:45:67:89:ac', 'id': 9},
    ]


def terms(request):
    if request.method == 'GET':
        return render(request, 'terms.html')
    elif request.method == 'HEAD':
        return HttpResponse()
    else:
        raise Exception('Invalid request method')


def devices(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['id'] is None:
                create_system(**form.cleaned_data)
            else:
                update_system(**form.cleaned_data)

            return HttpResponse('{"errors": []}')
        else:
            return HttpResponse422(json.dumps(form.errors))
    elif request.method == 'GET':
        devices = get_devices()
        return render(request, 'devices.html', {
            'devices': devices,
        })
    elif request.method == 'HEAD':
        return HttpResponse()
    else:
        raise Exception('Invalid request method')
