from hashlib import md5
from string import hexdigits
from time import time
from arim.conrad import Conrad
from arim.constants import (
    API_KEY, BASE_URL, USER_QUERY_KEY, SYSTEM_ENDPOINT, DESC_ATTR,
    SYSTEM_QUERY_KEY, DYNINTR_ENDPOINT, USER_ATTR, SYSTEM_NAME,
    SYSTEM_DETAIL_ENDPOINT, SYSTEM_ATTR_ENDPOINT, DYNINTR_RANGE, DYNINTR_CTNR)


class UserDeviceManager(object):
    @staticmethod
    def process_mac(mac):
        return filter(lambda x: x in hexdigits, mac)

    def __init__(self, user, api_client=None):
        self.username = user
        self.api_client = api_client or Conrad(API_KEY, BASE_URL)

    def get_all(self):
        """get all of the user's devices"""

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
            d = self.api_client.get(DYNINTR_ENDPOINT, query=query)
            if len(d):
                d = d[0]
            else:
                # Invalid device. We probably don't care about it.
                continue

            # pull dynamic intr MAC
            mac = d['mac']
            devices.append({
                'id': s['id'],
                'description': desc,
                'mac': mac,
            })

        return devices

    def get(self, pk):
        system = self.api_client.get(SYSTEM_ENDPOINT, pk=pk)

        # make sure the interface is the user's
        if next(
                filter(lambda x: x == USER_ATTR, system['systemav_set'])
        )['value'] != self.username:
            return False

        # get description
        desc = next(filter(lambda x: x['attribute'] == DESC_ATTR))['value']

        # find interface
        query = {SYSTEM_QUERY_KEY: system['id']}
        d = self.api_client.get(DYNINTR_ENDPOINT, query)

        # get MAC from interface
        mac = d['mac']

        device = {
            'id': system['id'],
            'description': desc,
            'mac': mac
        }

        return device

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