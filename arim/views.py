from django.http import HttpResponse
from django.shortcuts import render

from .forms import DeviceForm


def create_system(params):
    pass


def get_devices():
    return [{'name': 'Test system', 'mac': '01:23:45:67:89:ab'}]


def Terms(request):
    if request.method == 'GET':
        return render(request, 'terms.html')
    else:
        raise Exception('Invalid request method')


def Devices(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            submit_system({
                'description': form.description,
                'mac': form.mac,
            })
        else:
            return HttpResponse422(json.dumps(form.errors)
    else if request.method == 'GET':
        devices = get_devices()
        return render(request, 'devices.html', {
            'devices': devices,
        })
    else:
        raise Exception('Invalid request method')
