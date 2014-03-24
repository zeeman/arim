from django.db import models
from ipaddr import IPv4Address

from arim.settings import LEASE_TABLE


class Lease(models.Model):
    class Meta:
        db_table = LEASE_TABLE

    mac = models.CharField(max_length=17, db_index=True)
    ip = models.IntegerField(primary_key=True)
    date = models.IntegerField()

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __unicode__(self):
        return unicode(IPv4Address(self.ip)) + u' = ' + unicode(self.mac)

    def __repr__(self):
        return u'<Lease: ' + unicode(self) + u'>'
