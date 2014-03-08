import json
from hashlib import md5
from string import hexdigits
from time import time

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .conrad import Conrad
from .constants import *
from .forms import DeviceForm


class UserDeviceManager(object):
    @staticmethod
    def process_mac(mac):
        return filter(lambda x: x in hexdigits, mac)

    def __init__(self, user, api_client=None):
        self.username = user
        self.api_client = api_client or Conrad(API_KEY, BASE_URL)

    def get_all(self):
        # get all of the user's devices

        # first get the list of systems
        query = {USER_QUERY_KEY: self.username}
        systems = self.api_client.get(SYSTEM_ENDPOINT, query=query)
        while self.api_client.get_next():
            systems += self.api_client.result['results']

        # now add MAC info
        devices = []
        for s in systems:
            # get description (Hardware type)
            desc = next(
                iter(filter(lambda x: x['attribute'] == DESC_ATTR,
                            s['systemav_set']))
            )['value']

            # get MAC
            # find dynamic interface by system ID
            query = {SYSTEM_QUERY_KEY: s['id']}
            d = self.api_client.get(DYNINTR_ENDPOINT, query=query)[0]

            # pull dynamic intr MAC
            mac = d['mac']
            devices.append({
                'id': s['id'],
                'description': desc,
                'mac': mac,
            })

        return devices

    def create(self, description, mac):
        # preprocess MAC
        mac = self.process_mac(mac)

        # generate a unique identifier
        m = md5()
        m.update(mac + '-' + str(time()))
        hash = m.hexdigest()

        # create the new system
        system_data = {'name': SYSTEM_NAME.format(hash)}
        system_resp = self.api_client.post(SYSTEM_ENDPOINT, system_data)
        system_id = system_resp['id']

        # The entity field in the core/system/attributes endpoint is a
        # HyperlinkedRelatedField, so we have to send it the URL corresponding
        # to the system, instead of just a primary key.
        system_url = SYSTEM_DETAIL_ENDPOINT(system_id)

        # create other ID attribute
        other_id_data = {
            "entity": system_url,
            "attribute": USER_ATTR,
            "value": self.username
        }
        self.api_client.post(SYSTEM_ATTR_ENDPOINT, other_id_data)

        # create hardware type attribute
        hardware_type_data = {
            "entity": system_url,
            "attribute": DESC_ATTR,
            "value": description
        }
        self.api_client.post(SYSTEM_ATTR_ENDPOINT, hardware_type_data)

        # create dynamic intr
        interface_data = {
            "mac": mac,
            "range": DYNINTR_RANGE,
            "system": system_url,
            "ctnr": DYNINTR_CTNR
        }
        self.api_client.post(DYNINTR_ENDPOINT, interface_data)

    def update(self, pk, description, mac):
        # preprocess mac
        mac = self.process_mac(mac)

        # get the system
        system_data = self.api_client.get(SYSTEM_ENDPOINT, pk=pk)

        # make sure the interface is the user's
        owner = next(iter(
            filter(lambda x: x['attribute'] == USER_ATTR,
                   system_data['systemav_set']))
        )['value']
        if owner != self.username:
            return False

        # get description url
        # id is a HyperlinkedIdentityField so we don't need to process it
        hardware_type_url = next(
            iter(filter(lambda x: x['attribute'] == DESC_ATTR,
                        system_data['systemav_set']))
        )['id']

        # update hardware type (description)
        hardware_type_data = {"value": description}
        self.api_client.patch(hardware_type_url, pk=None,
                              data=hardware_type_data, verbatim=True)

        # find the dynamic interface
        interface_query = {SYSTEM_QUERY_KEY: system_data['id']}
        interface_data = self.api_client.get(DYNINTR_ENDPOINT,
                                             query=interface_query)[0]

        interface_update_data = {"mac": mac}
        self.api_client.patch(DYNINTR_ENDPOINT, pk=interface_data['id'],
                              data=interface_update_data)

    def delete(self, pk):
        # get the system
        system = self.api_client.get(SYSTEM_ENDPOINT, pk=pk)

        # make sure the interface is the user's
        if next(
                iter(filter(lambda x: x['attribute'] == USER_ATTR,
                            system['systemav_set']))
        )['value'] != self.username:
            return False

        # delete the system (the attrs and interface are deleted automatically)
        self.api_client.delete(SYSTEM_ENDPOINT, pk=pk)


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
        if not request.session.get('username', None):
            return redirect(login_view)
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


@require_login
def device_list_view(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            udm = UserDeviceManager(request.session.get('username'))

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
        udm = UserDeviceManager(request.session.get('username'))
        return render(request, 'device_list.html', {
            'devices': udm.get_all(),
            'logout_view': reverse('logout_view')
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
        udm = UserDeviceManager(request.session.get('username'))
        device = next(d for d in udm.get_all() if d['id'] == id)
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
        udm = UserDeviceManager(request.session.get('username'))
        udm.delete(id)
        return HttpResponse()
    else:
        raise Exception('Invalid request method')
