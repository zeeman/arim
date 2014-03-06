from django.conf import settings

MAX_DEVICES = 10  # The maximum number of devices to allow per user.

API_KEY = settings.API_KEY
BASE_URL = settings.BASE_URL

PK_QUERY_KEY = "i:id"
USER_QUERY_KEY = "a:Other ID"
DESC_QUERY_KEY = "a:Hardware+type"
SYSTEM_QUERY_KEY = "i:system"

USER_ATTR = "Other ID"
DESC_ATTR = "Hardware type"

SYSTEM_ENDPOINT = 'core/system'
SYSTEM_DETAIL_ENDPOINT = \
    lambda x: BASE_URL + SYSTEM_ENDPOINT + "/{}/".format(x)
SYSTEM_ATTR_ENDPOINT = 'core/system/attributes'
DYNINTR_ENDPOINT = 'dhcp/dynamic_interface'

DYNINTR_RANGE = BASE_URL + 'dhcp/range/188/'
DYNINTR_CTNR = BASE_URL + 'core/ctnr/107/'

SYSTEM_NAME = 'public-{}-Wireless'
