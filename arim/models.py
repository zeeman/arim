from django.db import models

from arim.settings import LEASE_TABLE


class Autoreg(models.Model):
    class Meta:
        db_table = LEASE_TABLE

    mac = models.CharField(max_length=17, db_index=True)
    ip = models.IntegerField(primary_key=True)
    date = models.IntegerField()
