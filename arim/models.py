from django.db import models


class Autoreg(models.Model):
    class Meta:
        db_table = 'autoreg'

    mac = models.CharField(max_length=17, db_index=True)
    ip = models.IntegerField(primary_key=True)
    date = models.IntegerField()
