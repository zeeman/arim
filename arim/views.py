import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render

from arim.udm import UserDeviceManager
from arim.models import Autoreg

from .forms import DeviceForm
from .utils import first, ip_str_to_long


def login_view(request):
    """
    View to handle user auth until we get Django CAS set up.
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        request.session['username'] = request.POST.get('username')
        return redirect(terms_view)
    else:
        raise Exception('Invalid request method')


def logout_view(request):
    if request.session['username']:
        del request.session['username']
    return redirect(login_view)


def require_login(view):
    def require_login_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(reverse('login_view'))
        return view(request, *args, **kwargs)
    return require_login_wrapper


@require_login
def terms_view(request):
    if request.method == 'GET':
        return render(request, 'terms.html')
    elif request.method == 'HEAD':
        return HttpResponse()
    else:
        raise Exception('Invalid request method')


def detect_mac(request):
    ip = ip_str_to_long(request.META.get('REMOTE_ADDR'))
    ar = Autoreg.objects.using('leases').filter(ip=ip).all()
    if len(ar):
        return ar[0].mac
    else:
        return None


@require_login
def device_list_view(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            udm = UserDeviceManager(request.user.username)

            if form.cleaned_data['id'] is None:
                # create_device(**form.cleaned_data)
                udm.create(form.cleaned_data['description'],
                           form.cleaned_data['mac'])
            else:
                # update_device(**form.cleaned_data)
                udm.update(form.cleaned_data['id'],
                           form.cleaned_data['description'],
                           form.cleaned_data['mac'])

            return HttpResponse('{"errors": []}')
        else:
            return HttpResponse(json.dumps(form.errors), status=422)
    elif request.method == 'GET':
        udm = UserDeviceManager(request.user.username)
        return render(request, 'device_list.html', {
            'devices': udm.get_all(),
            'logout_view': reverse('logout_view'),
            'user': request.user,
            'mac_address': detect_mac(request),
        })
    else:
        raise Exception('Invalid request method')


@require_login
def device_view(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if id is None:
            raise Exception('No id provided')
        id = int(id)
        udm = UserDeviceManager(request.user.username)
        device = first(ifilter(lambda d: d['id'] == id, udm.get_all()))
        return HttpResponse(json.dumps(device))
    else:
        raise Exception('Invalid request method')


@require_login
def delete_device_view(request):
    if request.method == 'POST':
        id = request.POST.get('id', None)
        if id is None:
            raise Exception('No id provided')
        id = int(id)
        udm = UserDeviceManager(request.user.username)
        udm.delete(id)
        return HttpResponse()
    else:
        raise Exception('Invalid request method')
