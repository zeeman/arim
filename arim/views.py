import json
from django.http import HttpResponse
from django.shortcuts import render

from .forms import DeviceForm


devices = [
    {'description': 'Test system', 'mac': '01:23:45:67:89:ab', 'id': 3},
    {'description': 'Test system 2', 'mac': '01:23:45:67:89:ac', 'id': 9},
]


def create_device(**kwargs):
    if devices:
        kwargs['id'] = max(d['id'] for d in devices) + 1
    else:
        kwargs['id'] = 0
    devices.append(kwargs)


def update_device(**kwargs):
    id = kwargs.pop('id', None)
    if id is None:
        raise Exception('No id provided')
    id = int(id)

    dev = next(d for d in devices if d['id'] == id)
    dev['description'] = kwargs['description']
    dev['mac'] = kwargs['mac']


def delete_device(id):
    global devices
    devices = [d for d in devices if d['id'] != id]



def get_devices():
    return devices


def terms_view(request):
    if request.method == 'GET':
        return render(request, 'terms.html')
    elif request.method == 'HEAD':
        return HttpResponse()
    else:
        raise Exception('Invalid request method')


def device_list_view(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['id'] is None:
                create_device(**form.cleaned_data)
            else:
                update_device(**form.cleaned_data)

            return HttpResponse('{"errors": []}')
        else:
            return HttpResponse(json.dumps(form.errors), status=422)
    elif request.method == 'GET':
        return render(request, 'device_list.html', {
            'devices': get_devices(),
        })
    else:
        raise Exception('Invalid request method')

def device_view(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if id is None:
            raise Exception('No id provided')
        id = int(id)
        device = next(d for d in devices if d['id'] == id)
        return HttpResponse(json.dumps(device))
    else:
        raise Exception('Invalid request method')


def delete_device_view(request):
    if request.method == 'POST':
        id = request.POST.get('id', None)
        if id is None:
            raise Exception('No id provided')
        id = int(id)
        delete_device(id)
        return HttpResponse()
    else:
        raise Exception('Invalid request method')
